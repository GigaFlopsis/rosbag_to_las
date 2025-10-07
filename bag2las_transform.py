import os
import rosbag
import laspy
import sensor_msgs.point_cloud2 as pc2
import numpy as np
from collections import defaultdict
import time
from scipy.spatial.distance import cdist
from scipy.interpolate import interp1d
from scipy.spatial import KDTree
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# TRANSFORMATION FUNCTIONS
# ============================================================================

def slerp_quaternions(q1, q2, t):
    """
    Spherical Linear Interpolation (SLERP) for quaternions.
    
    Parameters:
        q1: Starting quaternion [x, y, z, w]
        q2: Ending quaternion [x, y, z, w]
        t: Interpolation parameter [0, 1]
        
    Returns:
        np.array: Interpolated quaternion
    """
    # Ensure inputs are numpy arrays
    q1 = np.array(q1, dtype=np.float64)
    q2 = np.array(q2, dtype=np.float64)
    
    # Normalize quaternions
    q1 = q1 / np.linalg.norm(q1)
    q2 = q2 / np.linalg.norm(q2)
    
    # Compute the cosine of the angle between them
    dot = np.dot(q1, q2)
    
    # If the dot product is negative, slerp won't take the shorter path
    # So we negate one quaternion to correct this
    if dot < 0.0:
        q2 = -q2
        dot = -dot
    
    # If the inputs are too close for comfort, linearly interpolate
    DOT_THRESHOLD = 0.9995
    if dot > DOT_THRESHOLD:
        result = q1 + t * (q2 - q1)
        return result / np.linalg.norm(result)
    
    # Calculate the angle between the quaternions
    theta_0 = np.arccos(np.abs(dot))  # theta_0 = angle between input vectors
    sin_theta_0 = np.sin(theta_0)     # compute this only once
    theta = theta_0 * t               # theta = angle between v0 and result
    sin_theta = np.sin(theta)         # compute this only once
    
    # q2_perp = normalize(q2 - q1 * dot(q1, q2))
    s0 = np.cos(theta) - dot * sin_theta / sin_theta_0  # == sin(theta_0 - theta) / sin(theta_0)
    s1 = sin_theta / sin_theta_0
    
    return s0 * q1 + s1 * q2

def quaternion_to_rotation_matrix(quaternion):
    """
    Convert quaternion to 3x3 rotation matrix.
    
    Parameters:
        quaternion: [x, y, z, w] quaternion array
        
    Returns:
        np.array: 3x3 rotation matrix
    """
    x, y, z, w = quaternion
    
    # Normalize quaternion
    norm = np.sqrt(x*x + y*y + z*z + w*w)
    if norm > 0:
        x, y, z, w = x/norm, y/norm, z/norm, w/norm
    
    # Calculate rotation matrix elements
    rotation_matrix = np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
        [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)]
    ])
    
    return rotation_matrix

def create_transform_matrix(position, quaternion, lidar_offset=None):
    """
    Create 4x4 homogeneous transformation matrix from position and quaternion.
    
    Parameters:
        position: [x, y, z] position array
        quaternion: [x, y, z, w] quaternion array
        lidar_offset: Optional [x, y, z, rx, ry, rz] offset from robot base to lidar
        
    Returns:
        np.array: 4x4 transformation matrix
    """
    transform_matrix = np.eye(4)
    
    # Set rotation part
    transform_matrix[:3, :3] = quaternion_to_rotation_matrix(quaternion)
    
    # Set translation part
    transform_matrix[:3, 3] = position
    
    # Apply lidar offset if provided
    if lidar_offset is not None:
        # Create lidar offset matrix
        lidar_trans = lidar_offset[:3]  # Translation offset
        if len(lidar_offset) > 3:
            # Rotation offset (Euler angles in radians)
            rx, ry, rz = lidar_offset[3:6]
            # Create rotation matrix from Euler angles (ZYX convention)
            cos_rx, sin_rx = np.cos(rx), np.sin(rx)
            cos_ry, sin_ry = np.cos(ry), np.sin(ry)
            cos_rz, sin_rz = np.cos(rz), np.sin(rz)
            
            # ZYX Euler angle rotation matrix
            R_lidar = np.array([
                [cos_ry*cos_rz, -cos_ry*sin_rz, sin_ry],
                [sin_rx*sin_ry*cos_rz + cos_rx*sin_rz, -sin_rx*sin_ry*sin_rz + cos_rx*cos_rz, -sin_rx*cos_ry],
                [-cos_rx*sin_ry*cos_rz + sin_rx*sin_rz, cos_rx*sin_ry*sin_rz + sin_rx*cos_rz, cos_rx*cos_ry]
            ])
        else:
            R_lidar = np.eye(3)
        
        # Create lidar offset transformation matrix
        lidar_offset_matrix = np.eye(4)
        lidar_offset_matrix[:3, :3] = R_lidar
        lidar_offset_matrix[:3, 3] = lidar_trans
        
        # Apply offset: T_world_lidar = T_world_robot * T_robot_lidar
        transform_matrix = transform_matrix @ lidar_offset_matrix
    
    return transform_matrix

def apply_transform_to_points(points, transform_matrix):
    """
    Apply transformation matrix to point cloud.
    
    Parameters:
        points: Nx3 array of points [x, y, z]
        transform_matrix: 4x4 transformation matrix
        
    Returns:
        np.array: Transformed Nx3 points
    """
    # Validate inputs
    if points.shape[1] != 3:
        raise ValueError(f"Points must have 3 columns (x, y, z), got {points.shape[1]}")
    
    if transform_matrix.shape != (4, 4):
        raise ValueError(f"Transform matrix must be 4x4, got {transform_matrix.shape}")
    
    # Check for valid transformation matrix
    det = np.linalg.det(transform_matrix[:3, :3])
    if abs(det - 1.0) > 1e-3:
        print(f"⚠️  Warning: Transformation matrix determinant is {det:.6f}, expected ~1.0")
        print("   This may indicate scaling or reflection in the transformation")
    
    # Convert to homogeneous coordinates
    num_points = points.shape[0]
    homogeneous_points = np.ones((num_points, 4))
    homogeneous_points[:, :3] = points
    
    # Apply transformation
    transformed_homogeneous = (transform_matrix @ homogeneous_points.T).T
    
    # Convert back to 3D coordinates
    transformed_points = transformed_homogeneous[:, :3]
    
    # Validate output
    if np.any(np.isnan(transformed_points)) or np.any(np.isinf(transformed_points)):
        nan_count = np.isnan(transformed_points).sum()
        inf_count = np.isinf(transformed_points).sum()
        print(f"⚠️  Warning: Transformation produced {nan_count} NaN and {inf_count} inf values")
    
    return transformed_points

def validate_coordinate_systems(points_before, points_after, transform_description=""):
    """
    Validate coordinate system transformation.
    
    Parameters:
        points_before: Original points
        points_after: Transformed points
        transform_description: Description of the transformation
    """
    print(f"   🔍 Validating transformation: {transform_description}")
    
    # Check point count consistency
    if len(points_before) != len(points_after):
        print(f"   ❌ Point count mismatch: {len(points_before)} -> {len(points_after)}")
        return False
    
    # Calculate transformation statistics
    differences = points_after - points_before
    translation_distances = np.linalg.norm(differences, axis=1)
    
    print(f"   • Mean translation distance: {np.mean(translation_distances):.3f} m")
    print(f"   • Max translation distance: {np.max(translation_distances):.3f} m")
    print(f"   • Min translation distance: {np.min(translation_distances):.3f} m")
    
    # Check for reasonable bounds
    if np.max(translation_distances) > 1000:  # 1km threshold
        print(f"   ⚠️  Warning: Large transformation distances detected (max: {np.max(translation_distances):.1f} m)")
        print("   This may indicate coordinate system mismatch or incorrect odometry data")
    
    # Check coordinate ranges
    for axis, name in enumerate(['X', 'Y', 'Z']):
        before_range = np.max(points_before[:, axis]) - np.min(points_before[:, axis])
        after_range = np.max(points_after[:, axis]) - np.min(points_after[:, axis])
        range_change = abs(after_range - before_range) / max(before_range, 1e-6)
        
        if range_change > 0.1:  # 10% change threshold
            print(f"   ⚠️  Warning: {name} axis range changed by {range_change*100:.1f}% ({before_range:.3f} -> {after_range:.3f})")
    
    # Check for height (Z) issues specifically
    z_before_mean = np.mean(points_before[:, 2])
    z_after_mean = np.mean(points_after[:, 2])
    z_change = abs(z_after_mean - z_before_mean)
    
    if z_change > 2.0:  # 2 meter threshold
        print(f"   ⚠️  Warning: Significant Z (height) change: {z_before_mean:.3f} -> {z_after_mean:.3f} m")
        print("   This may indicate incorrect coordinate system assumptions")
    
    return True

def interpolate_odometry_data(pc_timestamps, odom_timestamps, odom_positions, odom_orientations):
    """
    Interpolate odometry data to match pointcloud timestamps.
    
    Parameters:
        pc_timestamps: Array of pointcloud timestamps
        odom_timestamps: Array of odometry timestamps  
        odom_positions: Nx3 array of odometry positions
        odom_orientations: Nx4 array of odometry quaternions
        
    Returns:
        tuple: (interpolated_positions, interpolated_orientations)
    """
    print("🔄 Интерполяция данных одометрии...")
    
    # Check if we have enough odometry data
    if len(odom_timestamps) < 2:
        print("⚠️  Недостаточно данных одометрии для интерполяции")
        return None, None
    
    # Find valid time range overlap
    odom_start = np.min(odom_timestamps)
    odom_end = np.max(odom_timestamps)
    pc_start = np.min(pc_timestamps)
    pc_end = np.max(pc_timestamps)
    
    print(f"   • Диапазон времени одометрии: {odom_start:.3f} - {odom_end:.3f}")
    print(f"   • Диапазон времени облака точек: {pc_start:.3f} - {pc_end:.3f}")
    
    # Check overlap
    overlap_start = max(odom_start, pc_start)
    overlap_end = min(odom_end, pc_end)
    
    if overlap_start >= overlap_end:
        print("❌ Нет временного перекрытия между данными одометрии и облаком точек")
        return None, None
    
    print(f"   • Область перекрытия: {overlap_start:.3f} - {overlap_end:.3f}")
    
    try:
        # Interpolate positions
        interp_x = interp1d(odom_timestamps, odom_positions[:, 0], 
                           kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_y = interp1d(odom_timestamps, odom_positions[:, 1], 
                           kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_z = interp1d(odom_timestamps, odom_positions[:, 2], 
                           kind='linear', bounds_error=False, fill_value='extrapolate')
        
        interpolated_positions = np.column_stack([
            interp_x(pc_timestamps),
            interp_y(pc_timestamps), 
            interp_z(pc_timestamps)
        ])
        
        # For quaternions, we need special handling - use SLERP instead of linear interpolation
        print("   🔄 Применение SLERP интерполяции для кватернионов...")
        interpolated_orientations = np.zeros((len(pc_timestamps), 4))
        
        for i, pc_time in enumerate(pc_timestamps):
            # Find the closest odometry timestamps
            if pc_time <= odom_timestamps[0]:
                # Use first quaternion
                interpolated_orientations[i] = odom_orientations[0]
            elif pc_time >= odom_timestamps[-1]:
                # Use last quaternion
                interpolated_orientations[i] = odom_orientations[-1]
            else:
                # Find surrounding points for SLERP
                idx = np.searchsorted(odom_timestamps, pc_time)
                if idx == 0:
                    idx = 1
                
                t1, t2 = odom_timestamps[idx-1], odom_timestamps[idx]
                q1, q2 = odom_orientations[idx-1], odom_orientations[idx]
                
                # Calculate interpolation parameter
                t = (pc_time - t1) / (t2 - t1) if t2 != t1 else 0.0
                t = np.clip(t, 0.0, 1.0)
                
                # Apply SLERP
                interpolated_orientations[i] = slerp_quaternions(q1, q2, t)
        
        print(f"   ✅ Интерполяция завершена для {len(pc_timestamps)} временных точек")
        
        return interpolated_positions, interpolated_orientations
        
    except Exception as e:
        print(f"❌ Ошибка интерполяции: {e}")
        return None, None

def collect_odometry_data(bag_file, odometry_topic):
    """
    Collect all odometry data from bag file.
    
    Parameters:
        bag_file: Path to bag file
        odometry_topic: Name of odometry topic
        
    Returns:
        tuple: (timestamps, positions, orientations)
    """
    print(f"🧭 Загрузка данных одометрии из топика '{odometry_topic}'...")
    
    timestamps = []
    positions = []
    orientations = []
    
    try:
        with rosbag.Bag(bag_file, 'r') as bag:
            total_messages = bag.get_message_count(topic_filters=odometry_topic)
            print(f"   📊 Всего сообщений одометрии: {total_messages:,}")
            
            if total_messages == 0:
                print("❌ Нет сообщений одометрии в выбранном топике")
                return None, None, None
            
            message_count = 0
            for topic, msg, ros_timestamp in bag.read_messages(topics=[odometry_topic]):
                message_count += 1
                
                # Extract timestamp
                timestamps.append(ros_timestamp.to_sec())
                
                # Extract position
                pos = msg.pose.pose.position
                positions.append([pos.x, pos.y, pos.z])
                
                # Extract orientation (quaternion)
                orient = msg.pose.pose.orientation
                orientations.append([orient.x, orient.y, orient.z, orient.w])
                
                # Progress indicator
                if message_count % max(1, total_messages // 10) == 0:
                    progress = (message_count / total_messages) * 100
                    print(f"   📊 [{progress:5.1f}%] Загружено {message_count:,}/{total_messages:,} сообщений")
            
            # Convert to numpy arrays
            timestamps = np.array(timestamps)
            positions = np.array(positions)
            orientations = np.array(orientations)
            
            print(f"   ✅ Загружены данные одометрии:")
            print(f"      • Временной диапазон: {np.min(timestamps):.3f} - {np.max(timestamps):.3f}")
            print(f"      • Общая дистанция: {calculate_total_distance(positions):.2f} м")
            
            return timestamps, positions, orientations
            
    except Exception as e:
        print(f"❌ Ошибка загрузки данных одометрии: {e}")
        return None, None, None

def calculate_total_distance(positions):
    """Calculate total distance traveled."""
    if len(positions) < 2:
        return 0.0
    distances = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))
    return np.sum(distances)

# ============================================================================
# SLAM FUNCTIONS
# ============================================================================

class SimpleSLAM:
    """
    Simplified SLAM implementation for pose graph optimization and loop closure detection.
    """
    
    def __init__(self, loop_closure_distance=2.0, min_time_gap=10.0):
        """
        Initialize SLAM parameters.
        
        Parameters:
            loop_closure_distance: Maximum distance to consider for loop closure
            min_time_gap: Minimum time gap between poses to consider for loop closure
        """
        self.loop_closure_distance = loop_closure_distance
        self.min_time_gap = min_time_gap
        self.poses = []  # List of poses [(timestamp, position, quaternion)]
        self.odometry_edges = []  # Odometry constraints
        self.loop_closure_edges = []  # Loop closure constraints
        
    def add_pose(self, timestamp, position, quaternion):
        """Add a pose to the graph."""
        pose_id = len(self.poses)
        self.poses.append((timestamp, np.array(position), np.array(quaternion)))
        
        # Add odometry edge to previous pose
        if pose_id > 0:
            self.odometry_edges.append((pose_id - 1, pose_id))
        
        return pose_id
    
    def detect_loop_closures(self, point_clouds=None):
        """
        Detect loop closures based on distance and optionally point cloud similarity.
        
        Parameters:
            point_clouds: Optional list of downsampled point clouds for each pose
            
        Returns:
            List of loop closure constraints (pose1_id, pose2_id, confidence)
        """
        print("🔍 Поиск замыканий циклов...")
        
        loop_closures = []
        num_poses = len(self.poses)
        
        if num_poses < 3:
            print("   ⚠️  Недостаточно поз для поиска циклов")
            return loop_closures
        
        # Build KDTree for efficient spatial queries
        positions = np.array([pose[1] for pose in self.poses])
        kdtree = KDTree(positions)
        
        for i in range(num_poses):
            current_time = self.poses[i][0]
            current_pos = self.poses[i][1]
            
            # Find nearby poses
            nearby_indices = kdtree.query_ball_point(current_pos, self.loop_closure_distance)
            
            for j in nearby_indices:
                if j <= i:  # Only look at previous poses
                    continue
                    
                # Check time gap constraint
                time_gap = abs(current_time - self.poses[j][0])
                if time_gap < self.min_time_gap:
                    continue
                
                # Calculate confidence based on distance
                distance = np.linalg.norm(current_pos - self.poses[j][1])
                confidence = max(0, 1.0 - distance / self.loop_closure_distance)
                
                # Additional point cloud similarity check if available
                if point_clouds is not None and i < len(point_clouds) and j < len(point_clouds):
                    pc_similarity = self._calculate_point_cloud_similarity(
                        point_clouds[i], point_clouds[j]
                    )
                    confidence *= pc_similarity
                
                if confidence > 0.3:  # Threshold for accepting loop closure
                    loop_closures.append((i, j, confidence))
                    print(f"   � Loop closure: поза {i} ↔ поза {j} (confidence: {confidence:.3f})")
        
        print(f"   ✅ Найдено {len(loop_closures)} замыканий циклов")
        self.loop_closure_edges = loop_closures
        return loop_closures
    
    def _calculate_point_cloud_similarity(self, pc1, pc2, max_points=1000):
        """
        Calculate similarity between two point clouds.
        
        Parameters:
            pc1, pc2: Point clouds as Nx3 arrays
            max_points: Maximum number of points to use for comparison
            
        Returns:
            Similarity score between 0 and 1
        """
        if pc1 is None or pc2 is None or len(pc1) == 0 or len(pc2) == 0:
            return 0.0
        
        # Downsample for efficiency
        if len(pc1) > max_points:
            indices = np.random.choice(len(pc1), max_points, replace=False)
            pc1 = pc1[indices]
        
        if len(pc2) > max_points:
            indices = np.random.choice(len(pc2), max_points, replace=False)
            pc2 = pc2[indices]
        
        try:
            # Simple geometric feature comparison
            # Calculate basic statistics for each point cloud
            stats1 = self._calculate_geometric_features(pc1)
            stats2 = self._calculate_geometric_features(pc2)
            
            # Compare features using normalized difference
            feature_diff = np.abs(stats1 - stats2) / (np.abs(stats1) + np.abs(stats2) + 1e-6)
            similarity = np.exp(-np.mean(feature_diff))
            
            return similarity
            
        except Exception as e:
            print(f"   ⚠️  Ошибка сравнения облаков: {e}")
            return 0.0
    
    def _calculate_geometric_features(self, pc):
        """Calculate basic geometric features of a point cloud."""
        if len(pc) == 0:
            return np.zeros(6)
        
        # Basic statistics
        mean_pos = np.mean(pc, axis=0)
        std_pos = np.std(pc, axis=0)
        
        return np.concatenate([mean_pos, std_pos])
    
    def optimize_poses(self, max_iterations=50):
        """
        Optimize the pose graph using least squares optimization.
        
        Returns:
            Optimized poses as list of (timestamp, position, quaternion)
        """
        print("🔧 Оптимизация графа поз...")
        
        if len(self.poses) < 2:
            print("   ⚠️  Недостаточно поз для оптимизации")
            return [pose for pose in self.poses]
        
        # Convert poses to optimization variables (x, y, z, qx, qy, qz, qw)
        initial_params = []
        for timestamp, position, quaternion in self.poses:
            initial_params.extend(position)  # x, y, z
            initial_params.extend(quaternion)  # qx, qy, qz, qw
        
        initial_params = np.array(initial_params)
        
        print(f"   📊 Оптимизация {len(self.poses)} поз с {len(self.odometry_edges)} одометрическими и {len(self.loop_closure_edges)} loop closure связями")
        
        try:
            # Run optimization
            result = least_squares(
                self._pose_graph_residuals,
                initial_params,
                max_nfev=max_iterations * len(initial_params),
                verbose=0
            )
            
            if result.success:
                print(f"   ✅ Оптимизация завершена за {result.nfev} итераций")
                print(f"   📈 Снижение ошибки: {result.fun[0]:.6f} → {result.fun[-1]:.6f}")
            else:
                print(f"   ⚠️  Оптимизация не сошлась: {result.message}")
            
            # Extract optimized poses
            optimized_poses = []
            for i in range(len(self.poses)):
                start_idx = i * 7
                position = result.x[start_idx:start_idx+3]
                quaternion = result.x[start_idx+3:start_idx+7]
                
                # Normalize quaternion
                quaternion = quaternion / np.linalg.norm(quaternion)
                
                optimized_poses.append((
                    self.poses[i][0],  # Keep original timestamp
                    position,
                    quaternion
                ))
            
            return optimized_poses
            
        except Exception as e:
            print(f"   ❌ Ошибка оптимизации: {e}")
            return [pose for pose in self.poses]
    
    def _pose_graph_residuals(self, params):
        """
        Calculate residuals for pose graph optimization.
        
        Parameters:
            params: Flattened array of pose parameters
            
        Returns:
            Array of residuals
        """
        residuals = []
        
        # Extract poses from parameters
        poses = []
        for i in range(len(self.poses)):
            start_idx = i * 7
            position = params[start_idx:start_idx+3]
            quaternion = params[start_idx+3:start_idx+7]
            poses.append((position, quaternion))
        
        # Odometry constraints
        for i, j in self.odometry_edges:
            if i < len(poses) and j < len(poses):
                # Calculate relative transformation
                rel_trans = poses[j][0] - poses[i][0]
                
                # Expected transformation based on original odometry
                expected_trans = self.poses[j][1] - self.poses[i][1]
                
                # Add residual for translation
                trans_residual = rel_trans - expected_trans
                residuals.extend(trans_residual)
                
                # Simple orientation constraint (could be improved)
                orient_residual = poses[j][1][:3] - poses[i][1][:3]  # Simplified
                residuals.extend(orient_residual * 0.1)  # Lower weight for orientation
        
        # Loop closure constraints
        for i, j, confidence in self.loop_closure_edges:
            if i < len(poses) and j < len(poses):
                # Loop closure should minimize distance between poses
                distance_residual = poses[i][0] - poses[j][0]
                residuals.extend(distance_residual * confidence)
        
        return np.array(residuals)
    
    def calculate_trajectory_metrics(self, original_poses, optimized_poses):
        """
        Calculate metrics to evaluate trajectory improvement.
        
        Returns:
            Dictionary with various metrics
        """
        if len(original_poses) != len(optimized_poses):
            return {}
        
        # Calculate total trajectory length before and after
        def trajectory_length(poses):
            length = 0.0
            for i in range(1, len(poses)):
                length += np.linalg.norm(poses[i][1] - poses[i-1][1])
            return length
        
        orig_length = trajectory_length(original_poses)
        opt_length = trajectory_length(optimized_poses)
        
        # Calculate drift (distance between start and end if it should be a loop)
        if len(self.loop_closure_edges) > 0:
            orig_drift = np.linalg.norm(original_poses[-1][1] - original_poses[0][1])
            opt_drift = np.linalg.norm(optimized_poses[-1][1] - optimized_poses[0][1])
        else:
            orig_drift = opt_drift = 0.0
        
        # Calculate average position change
        pos_changes = []
        for i in range(len(original_poses)):
            change = np.linalg.norm(optimized_poses[i][1] - original_poses[i][1])
            pos_changes.append(change)
        
        return {
            'original_length': orig_length,
            'optimized_length': opt_length,
            'original_drift': orig_drift,
            'optimized_drift': opt_drift,
            'average_position_change': np.mean(pos_changes),
            'max_position_change': np.max(pos_changes),
            'loop_closures_found': len(self.loop_closure_edges)
        }

def apply_slam_optimization(odom_timestamps, odom_positions, odom_orientations, 
                           point_clouds=None, enable_loop_closure=True):
    """
    Apply SLAM optimization to trajectory data.
    
    Parameters:
        odom_timestamps: Array of timestamps
        odom_positions: Nx3 array of positions
        odom_orientations: Nx4 array of quaternions
        point_clouds: Optional list of point clouds for loop closure detection
        enable_loop_closure: Whether to perform loop closure detection
        
    Returns:
        Tuple of (optimized_positions, optimized_orientations, metrics)
    """
    print("\n🤖 ПРИМЕНЕНИЕ SLAM ОПТИМИЗАЦИИ...")
    print("-" * 50)
    
    # Initialize SLAM system
    slam = SimpleSLAM(
        loop_closure_distance=3.0,  # 3 meters for loop closure detection
        min_time_gap=15.0           # 15 seconds minimum gap
    )
    
    # Add all poses to the graph
    print(f"📊 Добавление {len(odom_timestamps)} поз в граф...")
    for i in range(len(odom_timestamps)):
        slam.add_pose(odom_timestamps[i], odom_positions[i], odom_orientations[i])
    
    # Detect loop closures if enabled
    if enable_loop_closure:
        slam.detect_loop_closures(point_clouds)
    else:
        print("⚠️  Loop closure detection отключен")
    
    # Store original poses for comparison
    original_poses = [(odom_timestamps[i], odom_positions[i], odom_orientations[i]) 
                     for i in range(len(odom_timestamps))]
    
    # Optimize the pose graph
    optimized_poses = slam.optimize_poses()
    
    # Extract optimized data
    opt_positions = np.array([pose[1] for pose in optimized_poses])
    opt_orientations = np.array([pose[2] for pose in optimized_poses])
    
    # Calculate metrics
    metrics = slam.calculate_trajectory_metrics(original_poses, optimized_poses)
    
    # Print results
    print(f"\n� РЕЗУЛЬТАТЫ SLAM ОПТИМИЗАЦИИ:")
    print(f"   • Найдено loop closures: {metrics.get('loop_closures_found', 0)}")
    print(f"   • Исходная длина траектории: {metrics.get('original_length', 0):.2f} м")
    print(f"   • Оптимизированная длина: {metrics.get('optimized_length', 0):.2f} м")
    if metrics.get('loop_closures_found', 0) > 0:
        print(f"   • Исходный дрифт: {metrics.get('original_drift', 0):.3f} м")
        print(f"   • Оптимизированный дрифт: {metrics.get('optimized_drift', 0):.3f} м")
    print(f"   • Среднее изменение позиции: {metrics.get('average_position_change', 0):.3f} м")
    print(f"   • Максимальное изменение: {metrics.get('max_position_change', 0):.3f} м")
    
    return opt_positions, opt_orientations, metrics

def visualize_trajectory_comparison(original_positions, optimized_positions, slam_metrics, 
                                  output_dir, bag_filename):
    """
    Create visualization comparing original and optimized trajectories.
    
    Parameters:
        original_positions: Nx3 array of original positions
        optimized_positions: Nx3 array of optimized positions  
        slam_metrics: SLAM metrics dictionary
        output_dir: Directory to save plots
        bag_filename: Base filename for naming plots
    """
    try:
        print("📊 Создание визуализации траекторий...")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: 2D trajectory comparison (XY plane)
        ax1.plot(original_positions[:, 0], original_positions[:, 1], 
                'r-', alpha=0.7, linewidth=2, label='Исходная траектория')
        ax1.plot(optimized_positions[:, 0], optimized_positions[:, 1], 
                'b-', alpha=0.7, linewidth=2, label='Оптимизированная траектория')
        ax1.scatter(original_positions[0, 0], original_positions[0, 1], 
                   c='green', s=100, marker='o', label='Старт', zorder=5)
        ax1.scatter(original_positions[-1, 0], original_positions[-1, 1], 
                   c='red', s=100, marker='s', label='Финиш (исходный)', zorder=5)
        ax1.scatter(optimized_positions[-1, 0], optimized_positions[-1, 1], 
                   c='blue', s=100, marker='s', label='Финиш (оптимизированный)', zorder=5)
        ax1.set_xlabel('X (м)')
        ax1.set_ylabel('Y (м)')
        ax1.set_title('Сравнение траекторий (вид сверху)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # Plot 2: Height profile
        distances_orig = np.cumsum(np.concatenate([[0], np.sqrt(np.sum(np.diff(original_positions, axis=0)**2, axis=1))]))
        distances_opt = np.cumsum(np.concatenate([[0], np.sqrt(np.sum(np.diff(optimized_positions, axis=0)**2, axis=1))]))
        
        ax2.plot(distances_orig, original_positions[:, 2], 'r-', alpha=0.7, linewidth=2, label='Исходная')
        ax2.plot(distances_opt, optimized_positions[:, 2], 'b-', alpha=0.7, linewidth=2, label='Оптимизированная')
        ax2.set_xlabel('Расстояние по траектории (м)')
        ax2.set_ylabel('Высота Z (м)')
        ax2.set_title('Профиль высоты')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Position corrections
        position_changes = np.sqrt(np.sum((optimized_positions - original_positions)**2, axis=1))
        ax3.plot(position_changes, 'g-', linewidth=2)
        ax3.set_xlabel('Номер позиции')
        ax3.set_ylabel('Величина коррекции (м)')
        ax3.set_title('Коррекции позиций SLAM')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Metrics summary
        ax4.axis('off')
        
        # Prepare metrics text
        metrics_text = f"""РЕЗУЛЬТАТЫ SLAM ОПТИМИЗАЦИИ:

• Найдено замыканий циклов: {slam_metrics.get('loop_closures_found', 0)}

• Длина траектории:
  - Исходная: {slam_metrics.get('original_length', 0):.1f} м
  - Оптимизированная: {slam_metrics.get('optimized_length', 0):.1f} м

• Дрифт траектории:
  - Исходный: {slam_metrics.get('original_drift', 0):.3f} м
  - Оптимизированный: {slam_metrics.get('optimized_drift', 0):.3f} м

• Коррекции позиций:
  - Средняя: {slam_metrics.get('average_position_change', 0):.3f} м
  - Максимальная: {slam_metrics.get('max_position_change', 0):.3f} м

• Улучшения:
  - Снижение дрифта: {((slam_metrics.get('original_drift', 1) - slam_metrics.get('optimized_drift', 1)) / max(slam_metrics.get('original_drift', 1), 0.001) * 100):.1f}%
"""
        
        ax4.text(0.05, 0.95, metrics_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = os.path.join(output_dir, f"{bag_filename}_slam_trajectory_comparison.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Визуализация сохранена: {plot_filename}")
        
        return plot_filename
        
    except Exception as e:
        print(f"   ⚠️  Ошибка создания визуализации: {e}")
        return None

def choose_transform_mode():
    """
    Interactive function to choose transformation mode.
    
    Returns:
        tuple: (transform_mode, enable_slam) 
    """
    print(f"\n🎯 ВЫБОР РЕЖИМА ТРАНСФОРМАЦИИ:")
    print("=" * 60)
    print("1. 🚫 Без трансформации (оригинальные координаты сенсора)")
    print("2. 🌍 Глобальная система координат (одометрия)")
    print("3. 🌍 Глобальная система + SLAM оптимизация (рекомендуется)")
    print("4. 📍 Локальная система координат (относительно первого скана)")
    print("5. ❌ Отмена")
    print()
    
    while True:
        try:
            choice = input("Выберите режим трансформации (1-5): ").strip()
            
            if choice == "1":
                print("✅ Выбран режим: без трансформации")
                return "none", False
            elif choice == "2":
                print("✅ Выбран режим: глобальная система координат")
                return "global", False
            elif choice == "3":
                print("✅ Выбран режим: глобальная система + SLAM оптимизация")
                return "global", True
            elif choice == "4":
                print("✅ Выбран режим: локальная система координат")
                return "local", False
            elif choice == "5":
                print("❌ Отмена трансформации")
                return "none", False
            else:
                print("❌ Неверный выбор. Введите число от 1 до 5")
                
        except ValueError:
            print("❌ Ошибка ввода. Введите число")
        except KeyboardInterrupt:
            print("\n👋 Выбор прерван пользователем")
            return "none", False

def get_pointcloud2_topics(bag_file):
    """
    Function to find all PointCloud2 topics from a given bag file.

    Parameters:
        bag_file (str): Path to the ROS bag file.

    Returns:
        dict: Dictionary with topic names as keys and message counts as values
    """
    print("🔍 Scanning bag file for PointCloud2 topics...")
    # Dictionary to store occurrences of topics with PointCloud2 type
    pointcloud2_topics = defaultdict(int)
    
    with rosbag.Bag(bag_file, 'r') as bag:
        # Get total message count for progress
        try:
            total_msgs = bag.get_message_count()
            print(f"   📊 Analyzing {total_msgs:,} messages...")
        except:
            total_msgs = 0
            print("   📊 Analyzing messages...")
        
        msg_count = 0
        last_progress = -1
        
        for topic, msg, t in bag.read_messages():
            msg_count += 1
            if msg._type == 'sensor_msgs/PointCloud2':
                pointcloud2_topics[topic] += 1
            
            # Show progress every 5%
            if total_msgs > 0:
                progress = int((msg_count / total_msgs) * 100)
                if progress >= last_progress + 5:
                    print(f"   📈 Scan progress: {progress}% ({msg_count:,}/{total_msgs:,})")
                    last_progress = progress
    
    if pointcloud2_topics:
        print(f"   ✅ Found PointCloud2 topics: {dict(pointcloud2_topics)}")
        return dict(pointcloud2_topics)
    else:
        print("   ❌ No PointCloud2 topics found")
        return {}

def choose_pointcloud2_topic(bag_file):
    """
    Interactive function to choose PointCloud2 topic from available options.
    
    Parameters:
        bag_file (str): Path to the ROS bag file.
        
    Returns:
        str: Selected topic name, or None if no topics available or user cancelled
    """
    # Get all available PointCloud2 topics
    pointcloud2_topics = get_pointcloud2_topics(bag_file)
    
    if not pointcloud2_topics:
        print("❌ ERROR: No PointCloud2 topics found in the bag file")
        return None
    
    # If only one topic, use it automatically
    if len(pointcloud2_topics) == 1:
        topic_name = list(pointcloud2_topics.keys())[0]
        message_count = pointcloud2_topics[topic_name]
        print(f"✅ Only one PointCloud2 topic found: {topic_name} ({message_count:,} messages)")
        print("   🔄 Using automatically...")
        return topic_name
    
    # Multiple topics - let user choose
    print(f"\n🎯 ВЫБОР ТОПИКА PointCloud2:")
    print("=" * 60)
    print(f"Найдено {len(pointcloud2_topics)} топиков PointCloud2:")
    print()
    
    topics_list = list(pointcloud2_topics.items())
    
    # Display topics with statistics
    for i, (topic, count) in enumerate(topics_list, 1):
        # Get additional topic info
        try:
            with rosbag.Bag(bag_file, 'r') as bag:
                bag_info = bag.get_type_and_topic_info()
                if topic in bag_info.topics:
                    topic_info = bag_info.topics[topic]
                    frequency = topic_info.frequency
                    freq_str = f"~{frequency:.1f} Hz" if frequency is not None and frequency > 0 else "unknown Hz"
                else:
                    freq_str = "unknown Hz"
        except:
            freq_str = "unknown Hz"
        
        print(f"   {i}. 📡 {topic}")
        print(f"      📊 Сообщений: {count:,}")
        print(f"      🔄 Частота: {freq_str}")
        print()
    
    print("   0. ❌ Отмена")
    print()
    
    while True:
        try:
            choice = input(f"Выберите топик (0-{len(topics_list)}): ").strip()
            
            if choice == "0":
                print("❌ Выбор топика отменен")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(topics_list):
                selected_topic = topics_list[choice_num - 1][0]
                selected_count = topics_list[choice_num - 1][1]
                print(f"\n✅ Выбран топик: {selected_topic}")
                print(f"   📊 Сообщений к обработке: {selected_count:,}")
                
                # Confirm choice
                confirm = input(f"❓ Продолжить с этим топиком? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'д', 'да']:
                    return selected_topic
                else:
                    print("🔄 Выберите другой топик...")
                    continue
            else:
                print(f"❌ Неверный выбор. Введите число от 0 до {len(topics_list)}")
                
        except ValueError:
            print("❌ Ошибка ввода. Введите число")
        except KeyboardInterrupt:
            print("\n👋 Выбор прерван пользователем")
            return None

def get_topic_detailed_info(bag_file, topic_name):
    """
    Get detailed information about a specific topic.
    
    Parameters:
        bag_file (str): Path to the ROS bag file
        topic_name (str): Name of the topic to analyze
        
    Returns:
        dict: Detailed topic information
    """
    try:
        with rosbag.Bag(bag_file, 'r') as bag:
            bag_info = bag.get_type_and_topic_info()
            
            if topic_name not in bag_info.topics:
                return None
                
            topic_info = bag_info.topics[topic_name]
            
            # Get time range for this topic
            first_time = None
            last_time = None
            
            for topic, msg, t in bag.read_messages(topics=[topic_name]):
                if first_time is None:
                    first_time = t.to_sec()
                last_time = t.to_sec()
            
            duration = last_time - first_time if (first_time and last_time) else 0
            
            return {
                'message_count': topic_info.message_count,
                'msg_type': topic_info.msg_type,
                'frequency': topic_info.frequency,
                'first_time': first_time,
                'last_time': last_time,
                'duration': duration
            }
    except Exception as e:
        print(f"⚠️  Warning: Could not get detailed info for topic {topic_name}: {e}")
        return None

def get_odometry_topics(bag_file):
    """
    Function to find all Odometry topics from a given bag file.

    Parameters:
        bag_file (str): Path to the ROS bag file.

    Returns:
        dict: Dictionary with topic names as keys and message counts as values
    """
    print("🔍 Scanning bag file for Odometry topics...")
    odometry_topics = defaultdict(int)
    
    with rosbag.Bag(bag_file, 'r') as bag:
        try:
            total_msgs = bag.get_message_count()
            print(f"   📊 Analyzing {total_msgs:,} messages for odometry...")
        except:
            total_msgs = 0
            print("   📊 Analyzing messages for odometry...")
        
        msg_count = 0
        last_progress = -1
        
        for topic, msg, t in bag.read_messages():
            msg_count += 1
            if msg._type == 'nav_msgs/Odometry':
                odometry_topics[topic] += 1
            
            # Show progress every 10%
            if total_msgs > 0:
                progress = int((msg_count / total_msgs) * 100)
                if progress >= last_progress + 10:
                    print(f"   📈 Odometry scan progress: {progress}% ({msg_count:,}/{total_msgs:,})")
                    last_progress = progress
    
    if odometry_topics:
        print(f"   ✅ Found Odometry topics: {dict(odometry_topics)}")
        return dict(odometry_topics)
    else:
        print("   ❌ No Odometry topics found")
        return {}

def choose_odometry_topic(bag_file):
    """
    Interactive function to choose Odometry topic from available options.
    
    Parameters:
        bag_file (str): Path to the ROS bag file.
        
    Returns:
        str: Selected topic name, or None if no topics available or user cancelled
    """
    # Get all available Odometry topics
    odometry_topics = get_odometry_topics(bag_file)
    
    if not odometry_topics:
        print("❌ No Odometry topics found in the bag file")
        return None
    
    # If only one topic, use it automatically
    if len(odometry_topics) == 1:
        topic_name = list(odometry_topics.keys())[0]
        message_count = odometry_topics[topic_name]
        print(f"✅ Only one Odometry topic found: {topic_name} ({message_count:,} messages)")
        print("   🔄 Using automatically for .POS file generation...")
        return topic_name
    
    # Multiple topics - let user choose
    print(f"\n🎯 ВЫБОР ТОПИКА ODOMETRY:")
    print("=" * 60)
    print(f"Найдено {len(odometry_topics)} топиков Odometry:")
    print()
    
    topics_list = list(odometry_topics.items())
    
    # Display topics with statistics
    for i, (topic, count) in enumerate(topics_list, 1):
        try:
            with rosbag.Bag(bag_file, 'r') as bag:
                bag_info = bag.get_type_and_topic_info()
                if topic in bag_info.topics:
                    topic_info = bag_info.topics[topic]
                    frequency = topic_info.frequency
                    freq_str = f"~{frequency:.1f} Hz" if frequency is not None and frequency > 0 else "unknown Hz"
                else:
                    freq_str = "unknown Hz"
        except:
            freq_str = "unknown Hz"
        
        print(f"   {i}. 🧭 {topic}")
        print(f"      📊 Сообщений: {count:,}")
        print(f"      🔄 Частота: {freq_str}")
        print()
    
    print("   0. ❌ Пропустить создание .POS файла")
    print()
    
    while True:
        try:
            choice = input(f"Выберите топик одометрии (0-{len(topics_list)}): ").strip()
            
            if choice == "0":
                print("❌ Создание .POS файла пропущено")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(topics_list):
                selected_topic = topics_list[choice_num - 1][0]
                selected_count = topics_list[choice_num - 1][1]
                print(f"\n✅ Выбран топик одометрии: {selected_topic}")
                print(f"   📊 Сообщений к обработке: {selected_count:,}")
                return selected_topic
            else:
                print(f"❌ Неверный выбор. Введите число от 0 до {len(topics_list)}")
                
        except ValueError:
            print("❌ Ошибка ввода. Введите число")
        except KeyboardInterrupt:
            print("\n👋 Выбор прерван пользователем")
            return None

def create_pos_file(bag_file, output_dir, odometry_topic):
    """
    Create a .POS file from odometry data in the bag file.
    
    Parameters:
        bag_file (str): Path to the ROS bag file
        output_dir (str): Directory to save the .POS file
        odometry_topic (str): Name of the odometry topic to extract
    """
    if not odometry_topic:
        print("⚠️  No odometry topic provided, skipping .POS file creation")
        return
    
    try:
        print(f"\n🧭 СОЗДАНИЕ .POS ФАЙЛА...")
        print("-" * 50)
        print(f"📡 Источник: топик '{odometry_topic}'")
        
        # Extract base filename
        base_filename = os.path.splitext(os.path.basename(bag_file))[0]
        pos_file = os.path.join(output_dir, base_filename + ".pos")
        print(f"🎯 Выходной файл: {pos_file}")
        
        positions = []
        orientations = []
        timestamps = []
        
        print("🔄 Извлечение данных одометрии...")
        
        with rosbag.Bag(bag_file, 'r') as bag:
            # Get total message count for this topic
            total_messages = bag.get_message_count(topic_filters=odometry_topic)
            print(f"   📊 Всего сообщений одометрии: {total_messages:,}")
            
            if total_messages == 0:
                print("❌ Нет сообщений одометрии в выбранном топике")
                return
            
            message_count = 0
            start_time = time.time()
            
            for topic, msg, ros_timestamp in bag.read_messages(topics=[odometry_topic]):
                message_count += 1
                
                # Extract position
                pos = msg.pose.pose.position
                positions.append([pos.x, pos.y, pos.z])
                
                # Extract orientation (quaternion)
                orient = msg.pose.pose.orientation
                orientations.append([orient.x, orient.y, orient.z, orient.w])
                
                # Use ROS timestamp
                timestamps.append(ros_timestamp.to_sec())
                
                # Progress indicator
                if message_count % max(1, total_messages // 20) == 0 or message_count <= 5:
                    progress = (message_count / total_messages) * 100
                    print(f"   📊 [{progress:5.1f}%] Обработано {message_count:,}/{total_messages:,} сообщений")
        
        elapsed_time = time.time() - start_time
        print(f"   ⏱️  Извлечение завершено за {elapsed_time:.2f} секунд")
        
        # Convert to numpy arrays
        positions = np.array(positions)
        orientations = np.array(orientations)
        timestamps = np.array(timestamps)
        
        print(f"\n📊 АНАЛИЗ ТРАЕКТОРИИ:")
        print(f"   • Точек траектории: {len(positions):,}")
        print(f"   • Временной диапазон: {timestamps[-1] - timestamps[0]:.2f} секунд")
        print(f"   • Средняя частота: {len(positions) / (timestamps[-1] - timestamps[0]):.1f} Hz")
        
        # Calculate trajectory statistics
        if len(positions) > 1:
            distances = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))
            total_distance = np.sum(distances)
            max_distance_step = np.max(distances)
            avg_distance_step = np.mean(distances)
            
            print(f"   • Общая дистанция: {total_distance:.2f} м")
            print(f"   • Макс. шаг: {max_distance_step:.3f} м")
            print(f"   • Средний шаг: {avg_distance_step:.3f} м")
        
        # Position ranges
        print(f"   • Диапазон X: {np.min(positions[:, 0]):.6f} до {np.max(positions[:, 0]):.6f}")
        print(f"   • Диапазон Y: {np.min(positions[:, 1]):.6f} до {np.max(positions[:, 1]):.6f}")
        print(f"   • Диапазон Z: {np.min(positions[:, 2]):.6f} до {np.max(positions[:, 2]):.6f}")
        
        # Convert quaternions to Euler angles (roll, pitch, yaw)
        def quaternion_to_euler(q):
            """Convert quaternion to euler angles (roll, pitch, yaw) in degrees"""
            x, y, z, w = q
            
            # Roll (x-axis rotation)
            sinr_cosp = 2 * (w * x + y * z)
            cosr_cosp = 1 - 2 * (x * x + y * y)
            roll = np.arctan2(sinr_cosp, cosr_cosp)
            
            # Pitch (y-axis rotation)
            sinp = 2 * (w * y - z * x)
            if np.abs(sinp) >= 1:
                pitch = np.copysign(np.pi / 2, sinp)  # use 90 degrees if out of range
            else:
                pitch = np.arcsin(sinp)
            
            # Yaw (z-axis rotation)
            siny_cosp = 2 * (w * z + x * y)
            cosy_cosp = 1 - 2 * (y * y + z * z)
            yaw = np.arctan2(siny_cosp, cosy_cosp)
            
            return np.degrees([roll, pitch, yaw])
        
        print("🔄 Конвертация кватернионов в углы Эйлера...")
        euler_angles = np.array([quaternion_to_euler(q) for q in orientations])
        
        print(f"   • Диапазон Roll: {np.min(euler_angles[:, 0]):.2f}° до {np.max(euler_angles[:, 0]):.2f}°")
        print(f"   • Диапазон Pitch: {np.min(euler_angles[:, 1]):.2f}° до {np.max(euler_angles[:, 1]):.2f}°")
        print(f"   • Диапазон Yaw: {np.min(euler_angles[:, 2]):.2f}° до {np.max(euler_angles[:, 2]):.2f}°")
        
        # Write .POS file
        print(f"\n💾 ЗАПИСЬ .POS ФАЙЛА...")
        
        with open(pos_file, 'w') as f:
            # Write header
            f.write("% POS file generated from ROS bag odometry data\n")
            f.write(f"% Source bag: {os.path.basename(bag_file)}\n")
            f.write(f"% Odometry topic: {odometry_topic}\n")
            f.write(f"% Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("% Format: GPS_Time X Y Z Roll Pitch Yaw\n")
            f.write("% Units: seconds, meters, degrees\n")
            f.write("%\n")
            
            # Write data
            for i in range(len(positions)):
                gps_time = timestamps[i]
                x, y, z = positions[i]
                roll, pitch, yaw = euler_angles[i]
                
                f.write(f"{gps_time:.6f} {x:.6f} {y:.6f} {z:.6f} {roll:.6f} {pitch:.6f} {yaw:.6f}\n")
        
        # Verify file creation
        if os.path.exists(pos_file):
            file_size = os.path.getsize(pos_file)
            print(f"✅ .POS файл создан успешно!")
            print(f"   📁 Файл: {pos_file}")
            print(f"   📊 Размер: {file_size:,} байт")
            print(f"   🔢 Записей: {len(positions):,}")
            
            # Verify by reading first and last few lines
            with open(pos_file, 'r') as f:
                lines = f.readlines()
                data_lines = [line for line in lines if not line.startswith('%')]
                print(f"   ✅ Проверка: {len(data_lines)} строк данных")
                
                if len(data_lines) >= 3:
                    print(f"   🔍 Первая запись: {data_lines[0].strip()}")
                    print(f"   🔍 Последняя запись: {data_lines[-1].strip()}")
        else:
            print("❌ Ошибка: .POS файл не был создан")
    
    except Exception as e:
        print(f"❌ Ошибка создания .POS файла: {e}")
        import traceback
        traceback.print_exc()

def choose_express_mode():
    """
    Ask user if they want to use express mode with default parameters.
    
    Returns:
        bool: True if express mode selected
    """
    print(f"\n⚡ ЭКСПРЕСС-РЕЖИМ:")
    print("=" * 60)
    print("Использовать стандартные параметры?")
    print("  • Топик облака точек: /cloud_registered")
    print("  • Топик одометрии: /lio/odom")
    print("  • Режим трансформации: Без трансформации")
    print()
    print("1. ⚡ Да, использовать экспресс-режим")
    print("2. ⚙️  Нет, настроить вручную")
    print()
    
    while True:
        try:
            choice = input("Выберите режим (1-2): ").strip()
            
            if choice == "1":
                print("✅ Выбран экспресс-режим")
                return True
            elif choice == "2":
                print("✅ Выбрана ручная настройка")
                return False
            else:
                print("❌ Неверный выбор. Введите 1 или 2")
                
        except KeyboardInterrupt:
            print("\n👋 Выбор прерван пользователем")
            return False

def convert_bag_to_laz(bag_file, output_dir, selected_topic=None, transform_mode=None, enable_slam=None, express_mode=False):
    """
    Function to convert PointCloud2 data from a ROS bag file to a LAZ file with optional transformation and SLAM optimization.

    Parameters:
        bag_file (str): Path to the ROS bag file.
        output_dir (str): Directory to save the generated LAZ files.
        selected_topic (str): Specific topic to process (if None, will prompt user to choose)
        transform_mode (str): Transformation mode ('none', 'global', 'local', None for user choice)
        enable_slam (bool): Whether to enable SLAM optimization (None for user choice)
        express_mode (bool): Use express mode with default parameters
    """
    try:
        print("="*80)
        print(f"STARTING CONVERSION: {os.path.basename(bag_file)}")
        print("="*80)
        
        # First, analyze all topics in the bag file
        bag_analysis = analyze_bag_topics(bag_file)
        
        if not bag_analysis:
            print("❌ ERROR: Could not analyze bag file")
            return
        
        # Ask about express mode if not already set
        if not express_mode and selected_topic is None:
            express_mode = choose_express_mode()
        
        # Apply express mode defaults
        if express_mode:
            print("\n⚡ ПРИМЕНЕНИЕ ЭКСПРЕСС-РЕЖИМА...")
            
            # Check if default topics exist
            available_pc_topics = get_pointcloud2_topics(bag_file)
            available_odom_topics = get_odometry_topics(bag_file)
            
            # Set default pointcloud topic
            if selected_topic is None:
                if "/cloud_registered" in available_pc_topics:
                    selected_topic = "/cloud_registered"
                    print(f"✅ Топик облака точек: {selected_topic}")
                else:
                    print(f"⚠️  Топик /cloud_registered не найден")
                    print(f"   Доступные топики: {list(available_pc_topics.keys())}")
                    selected_topic = choose_pointcloud2_topic(bag_file)
            
            # Set default odometry topic
            if "/lio/odom" in available_odom_topics:
                odometry_topic = "/lio/odom"
                print(f"✅ Топик одометрии: {odometry_topic}")
            else:
                print(f"⚠️  Топик /lio/odom не найден")
                print(f"   Доступные топики: {list(available_odom_topics.keys())}")
                odometry_topic = choose_odometry_topic(bag_file)
            
            # Set default transformation mode
            if transform_mode is None:
                transform_mode = "none"
                enable_slam = False
                print(f"✅ Режим трансформации: без трансформации")
        else:
            # Wait for user to review the analysis
            input("\n📋 Нажмите Enter для продолжения обработки...")
            odometry_topic = None
        
        # Choose the PointCloud2 topic (if not set by express mode)
        if selected_topic is None:
            pointcloud2_topic = choose_pointcloud2_topic(bag_file)
            if not pointcloud2_topic:
                print("❌ ERROR: No topic selected or no PointCloud2 topics available")
                return
        else:
            # Verify the specified topic exists and is PointCloud2
            available_topics = get_pointcloud2_topics(bag_file)
            if selected_topic not in available_topics:
                print(f"❌ ERROR: Topic '{selected_topic}' not found in available PointCloud2 topics")
                print(f"Available topics: {list(available_topics.keys())}")
                return
            pointcloud2_topic = selected_topic
        
        print(f"✅ Processing topic: {pointcloud2_topic}")
        
        # Choose odometry topic for .POS file and transformation (if not set by express mode)
        if not express_mode:
            print(f"\n🧭 ПОИСК ТОПИКОВ ОДОМЕТРИИ...")
            odometry_topic = choose_odometry_topic(bag_file)
        
        # Choose transformation mode (if not set by express mode)
        if transform_mode is None or enable_slam is None:
            if odometry_topic:
                transform_mode, enable_slam = choose_transform_mode()
            else:
                print("⚠️  Нет топиков одометрии - трансформация недоступна")
                transform_mode = "none"
                enable_slam = False
        
        print(f"🔧 Режим трансформации: {transform_mode}")
        if enable_slam:
            print("🤖 SLAM оптимизация: включена")
        
        # Load odometry data if transformation is needed
        odom_timestamps = None
        odom_positions = None 
        odom_orientations = None
        slam_metrics = None
        
        if transform_mode in ["global", "local"] and odometry_topic:
            print(f"\n🔄 ЗАГРУЗКА ДАННЫХ ОДОМЕТРИИ...")
            odom_timestamps, odom_positions, odom_orientations = collect_odometry_data(bag_file, odometry_topic)
            
            if odom_timestamps is None:
                print("❌ Не удалось загрузить данные одометрии, используется режим без трансформации")
                transform_mode = "none"
                enable_slam = False
            elif enable_slam and transform_mode == "global":
                # Save original positions for visualization
                odom_positions_original = odom_positions.copy()
                odom_orientations_original = odom_orientations.copy()
                
                # Apply SLAM optimization
                odom_positions, odom_orientations, slam_metrics = apply_slam_optimization(
                    odom_timestamps, odom_positions, odom_orientations, 
                    point_clouds=None,  # Will be populated during processing if needed
                    enable_loop_closure=True
                )
        
        # Get detailed topic information
        topic_details = get_topic_detailed_info(bag_file, pointcloud2_topic)
        if topic_details:
            print(f"📊 Topic details:")
            print(f"   • Messages: {topic_details['message_count']:,}")
            print(f"   • Frequency: ~{topic_details['frequency']:.2f} Hz")
            if topic_details['duration'] > 0:
                print(f"   • Duration: {topic_details['duration']:.2f} seconds")
                print(f"   • Time range: {topic_details['first_time']:.3f} - {topic_details['last_time']:.3f}")
        
        # Open the ROS bag file
        print(f"📂 Opening ROS bag file: {bag_file}")
        bag = rosbag.Bag(bag_file, 'r')

        # Get bag info with progress
        print("📊 Analyzing bag file structure...")
        bag_info = bag.get_type_and_topic_info()
        print(f"   • Total topics: {len(bag_info.topics)}")
        if pointcloud2_topic in bag_info.topics:
            topic_info = bag_info.topics[pointcloud2_topic]
            print(f"   • PointCloud2 messages: {topic_info.message_count}")
            print(f"   • Message type: {topic_info.msg_type}")
            freq_display = f"~{topic_info.frequency:.2f} Hz" if topic_info.frequency is not None else "unknown Hz"
            print(f"   • Frequency: {freq_display}")

        # Get the total number of messages in the bag file
        print("📈 Counting PointCloud2 messages...")
        total_messages = bag.get_message_count(topic_filters=pointcloud2_topic)
        print(f"   ✅ Total messages to process: {total_messages}")

        # Create empty lists to store coordinates and additional fields
        x_list = []
        y_list = []
        z_list = []
        intensity_list = []
        gps_time_list = []

        # Initialize counters and statistics
        message_count = 0
        total_points = 0
        points_per_message = []

        print("\n🔍 ANALYZING MESSAGE STRUCTURE...")
        print("-" * 50)
        
        # Check available fields in the first message
        print("🔎 Reading first message for field analysis...")
        first_msg = None
        first_points_sample = []
        
        for _, msg, _ in bag.read_messages(topics=[pointcloud2_topic]):
            first_msg = msg
            print("   ✅ First message loaded")
            
            # Try to read a few points to check data format
            try:
                point_count = 0
                for point in pc2.read_points(msg, skip_nans=False):  # Don't skip NaNs initially
                    first_points_sample.append(point)
                    point_count += 1
                    if point_count >= 10:  # Read first 10 points
                        break
                print(f"   ✅ Successfully read {len(first_points_sample)} sample points")
                
                # Check for NaN patterns
                if first_points_sample:
                    first_point = first_points_sample[0]
                    print(f"   🔍 First point structure: {len(first_point)} fields")
                    print(f"   🔍 First point values: {first_point}")
                    
                    # Check for NaN values in sample
                    nan_count = 0
                    for point in first_points_sample:
                        if any(np.isnan(val) if isinstance(val, float) else False for val in point[:3]):
                            nan_count += 1
                    print(f"   📊 NaN points in sample: {nan_count}/{len(first_points_sample)}")
                    
            except Exception as e:
                print(f"   ⚠️  Error reading sample points: {e}")
                
            break
        
        if not first_msg:
            print("❌ ERROR: Could not read first message")
            return

        available_fields = [field.name for field in first_msg.fields] if first_msg else []
        print(f"📋 Available fields ({len(available_fields)}): {available_fields}")
        
        # Add OS and library version info
        import platform
        print(f"\n🖥️  SYSTEM INFO:")
        print(f"   • OS: {platform.system()} {platform.release()}")
        print(f"   • Python: {platform.python_version()}")
        try:
            import sensor_msgs
            print(f"   • sensor_msgs version: {sensor_msgs.__version__ if hasattr(sensor_msgs, '__version__') else 'unknown'}")
        except:
            print(f"   • sensor_msgs version: unknown")
        print(f"   • numpy version: {np.__version__}")
        try:
            print(f"   • laspy version: {laspy.__version__}")
        except:
            print(f"   • laspy version: unknown")
        
        # Print detailed field information for debugging
        if first_msg:
            print("\n📊 Detailed field information:")
            for i, field in enumerate(first_msg.fields):
                datatype_names = {1: 'INT8', 2: 'UINT8', 3: 'INT16', 4: 'UINT16', 
                                5: 'INT32', 6: 'UINT32', 7: 'FLOAT32', 8: 'FLOAT64'}
                datatype_name = datatype_names.get(field.datatype, f'UNKNOWN({field.datatype})')
                print(f"   {i+1:2d}. {field.name:15s} | Type: {datatype_name:8s} | Offset: {field.offset:3d} | Count: {field.count}")
            
            print(f"\n📐 PointCloud2 dimensions:")
            print(f"   • Width: {first_msg.width}")
            print(f"   • Height: {first_msg.height}")
            print(f"   • Points per message: {first_msg.width * first_msg.height}")
            print(f"   • Point step: {first_msg.point_step} bytes")
            print(f"   • Row step: {first_msg.row_step} bytes")
            print(f"   • Is dense: {first_msg.is_dense}")
            
            # Check if message has header with timestamp
            if hasattr(first_msg, 'header') and hasattr(first_msg.header, 'stamp'):
                timestamp = first_msg.header.stamp.to_sec()
                print(f"   • Header timestamp: {timestamp:.6f} ({timestamp})")
                print(f"   • Frame ID: '{first_msg.header.frame_id}'")
                print("✅ Will use ROS header timestamp as GPS time")
        
        # Determine which fields to extract based on availability
        fields_to_extract = ["x", "y", "z"]
        has_intensity = "intensity" in available_fields
        
        # Expanded search for time fields in PointCloud2 data
        possible_time_fields = ["gps_time", "time", "t", "timestamp", "time_stamp", "stamp"]
        has_pointcloud_time = False
        pointcloud_time_field = None
        
        for field_name in possible_time_fields:
            if field_name in available_fields:
                has_pointcloud_time = True
                pointcloud_time_field = field_name
                print(f"⏰ PointCloud2 time field found: {pointcloud_time_field}")
                break
        
        # Use ROS header timestamp if no time field in PointCloud2
        use_ros_time = not has_pointcloud_time and hasattr(first_msg, 'header')
        has_gps_time = has_pointcloud_time or use_ros_time
        
        print(f"\n🎯 FIELD EXTRACTION PLAN:")
        print(f"   • Coordinates (x,y,z): ✅ Always included")
        
        if has_intensity:
            fields_to_extract.append("intensity")
            print(f"   • Intensity: ✅ Found in PointCloud2")
        else:
            print(f"   • Intensity: ❌ Not found")
            
        if has_pointcloud_time:
            fields_to_extract.append(pointcloud_time_field)
            print(f"   • Time: ✅ From PointCloud2 field '{pointcloud_time_field}'")
        elif use_ros_time:
            print(f"   • Time: ✅ From ROS header timestamp")
        else:
            print(f"   • Time: ❌ No time information available")

        print(f"\n📝 Fields to extract: {fields_to_extract}")

        print(f"\n🔄 PROCESSING MESSAGES...")
        print("-" * 50)

        # Reset bag reading
        bag.close()
        print("🔄 Reopening bag file for processing...")
        bag = rosbag.Bag(bag_file, 'r')

        # Initialize progress tracking and transformation data
        processed_points = 0
        start_time = time.time()
        print(f"⏱️  Processing started at {time.strftime('%H:%M:%S')}")
        
        # Store message timestamps for transformation
        message_timestamps = []
        message_points_data = []
        
        # First pass: collect all data and timestamps
        print(f"🔄 First pass: collecting point cloud data...")
        
        for _, msg, ros_timestamp in bag.read_messages(topics=[pointcloud2_topic]):
            # Increment the counter for processed messages
            message_count += 1
            
            # Calculate message timestamp for ROS time usage
            message_time = ros_timestamp.to_sec()
            message_timestamps.append(message_time)
            
            # Debug message structure on first few messages
            if message_count <= 3:
                print(f"\n🔍 DEBUG Message {message_count}:")
                print(f"   • Width: {msg.width}, Height: {msg.height}")
                print(f"   • Point step: {msg.point_step}, Row step: {msg.row_step}")
                print(f"   • Expected points: {msg.width * msg.height}")
                print(f"   • Data length: {len(msg.data)} bytes")
                print(f"   • Is dense: {msg.is_dense}")
                print(f"   • Message timestamp: {message_time:.6f}")
                
            # Count points in this message first to calculate time increments
            points_in_message = []
            points_read = 0
            
            try:
                for point in pc2.read_points(msg, field_names=fields_to_extract, skip_nans=True):
                    points_in_message.append(point)
                    points_read += 1
                    
                    # Debug first few points of first message
                    if message_count <= 2 and points_read <= 5:
                        print(f"      Point {points_read}: {[f'{x:.6f}' if isinstance(x, float) else x for x in point]}")
                        
            except Exception as e:
                print(f"   ❌ Error reading points from message {message_count}: {e}")
                continue
            
            message_points_data.append(points_in_message)
            message_points = len(points_in_message)
            
            if message_count <= 3:
                print(f"   • Actually read points: {message_points}")
                print(f"   • Points extraction ratio: {message_points / (msg.width * msg.height) * 100:.1f}%")
                print(f"   • Point data sample: {points_in_message[:3]}")
            
            # Enhanced progress indicator with percentage bar
            progress = (message_count / total_messages) * 100
            elapsed_time = time.time() - start_time
            
            # Show progress more frequently for small files, less for large files
            if total_messages <= 10:
                show_progress = True
            elif total_messages <= 100:
                show_progress = (message_count % 5 == 0) or (message_count <= 3) or (message_count == total_messages)
            else:
                show_progress = (message_count % max(1, total_messages // 20) == 0) or (message_count <= 3) or (message_count == total_messages)
            
            if show_progress:
                # Calculate ETA
                if message_count > 1:
                    avg_time_per_msg = elapsed_time / message_count
                    eta_seconds = (total_messages - message_count) * avg_time_per_msg
                    eta_str = f"ETA: {int(eta_seconds//60):02d}:{int(eta_seconds%60):02d}"
                else:
                    eta_str = "ETA: --:--"
                
                # Create progress bar
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                print(f"   📊 [{bar}] {progress:5.1f}% | Msg {message_count:4d}/{total_messages} | {message_points:,} pts | {eta_str}")
                
                # Show points processing rate
                if processed_points > 0 and elapsed_time > 0:
                    points_per_sec = processed_points / elapsed_time
                    print(f"       ⚡ Processing rate: {points_per_sec:,.0f} points/sec | Elapsed: {int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}")
            else:
                print(f"   📊 [{progress:5.1f}%] Processing message {message_count:4d}/{total_messages} - {message_points:,} points")

            points_per_message.append(message_points)
            total_points += message_points
            processed_points += message_points

        # Final progress update
        final_elapsed = time.time() - start_time
        print(f"\n   🏁 Data collection completed in {int(final_elapsed//60):02d}:{int(final_elapsed%60):02d}")
        print(f"   ⚡ Average processing rate: {total_points/final_elapsed:,.0f} points/sec")
        
        # Prepare transformation if needed
        reference_transform = None
        if transform_mode in ["global", "local"] and odom_timestamps is not None:
            print(f"\n🔧 ПОДГОТОВКА ТРАНСФОРМАЦИИ...")
            
            # Convert message timestamps to numpy array
            message_timestamps = np.array(message_timestamps)
            
            # Interpolate odometry data to match message timestamps
            interp_positions, interp_orientations = interpolate_odometry_data(
                message_timestamps, odom_timestamps, odom_positions, odom_orientations
            )
            
            if interp_positions is None:
                print("❌ Не удалось интерполировать данные одометрии, используется режим без трансформации")
                transform_mode = "none"
            else:
                print(f"   ✅ Данные одометрии интерполированы для {len(message_timestamps)} сообщений")
                
                # For local mode, calculate reference transform from first message
                if transform_mode == "local":
                    reference_transform = create_transform_matrix(
                        interp_positions[0], interp_orientations[0]
                    )
                    # Invert reference transform to get transformation TO reference frame
                    reference_transform = np.linalg.inv(reference_transform)
                    print(f"   🎯 Локальная система координат установлена на основе первого скана")
        
        # Second pass: process points with transformation
        print(f"\n🔄 Second pass: processing and transforming points...")
        start_time = time.time()
        
        # Calculate time increment per point if using ROS time
        time_increment = 0
        if use_ros_time and len(message_points_data) > 1:
            # Option 1: Use message timestamp for all points (uniform coloring per scan)
            # Option 2: Create sequential time across all points
            # We'll use Option 1 for now - all points in message get same timestamp
            time_increment = 0  # No increment within message
            print(f"   ⏱️  Using uniform timestamp per message for better visualization")

        # Process each message with its interpolated transform
        for msg_idx, points_in_message in enumerate(message_points_data):
            message_time = message_timestamps[msg_idx]
            
            # Get transformation matrix for this message
            transform_matrix = None
            if transform_mode == "global" and interp_positions is not None:
                transform_matrix = create_transform_matrix(
                    interp_positions[msg_idx], interp_orientations[msg_idx]
                )
            elif transform_mode == "local" and interp_positions is not None:
                msg_transform = create_transform_matrix(
                    interp_positions[msg_idx], interp_orientations[msg_idx]
                )
                # Transform relative to reference (first scan)
                transform_matrix = reference_transform @ msg_transform
            
            # Extract points for this message
            msg_points = []
            for point_idx, point in enumerate(points_in_message):
                # Debug first 3 points of first message
                if msg_idx == 0 and point_idx < 3:
                    print(f"      Point {point_idx}: {[f'{x:.6f}' if isinstance(x, float) else x for x in point]}")
                
                # Extract coordinates
                point_coords = np.array([point[0], point[1], point[2]])
                msg_points.append(point_coords)
                
                # Store other fields for later use
                field_idx = 3
                if has_intensity:
                    intensity_val = point[field_idx] if len(point) > field_idx else 0
                    intensity_list.append(intensity_val)
                    if msg_idx == 0 and point_idx < 3:
                        print(f"         └─ Intensity at index {field_idx}: {intensity_val}")
                    field_idx += 1
                    
                if has_pointcloud_time:
                    time_val = point[field_idx] if len(point) > field_idx else 0
                    gps_time_list.append(time_val)
                    if msg_idx == 0 and point_idx < 3:
                        print(f"         └─ PointCloud time at index {field_idx}: {time_val}")
                elif use_ros_time:
                    # Use message timestamp for all points in the message
                    # This creates clear temporal separation between scans
                    gps_time_list.append(message_time)
                    if msg_idx == 0 and point_idx < 3:
                        print(f"         └─ ROS time: {message_time:.6f} (uniform for message)")
            
            # Apply transformation to all points in this message if needed
            if len(msg_points) > 0:
                msg_points = np.array(msg_points)
                
                if transform_matrix is not None:
                    if msg_idx == 0:
                        print(f"   🔧 Применение трансформации к точкам...")
                        print(f"      • Режим: {transform_mode}")
                        if transform_mode == "global":
                            print(f"      • Трансформация в глобальную систему координат")
                        elif transform_mode == "local":
                            print(f"      • Трансформация относительно первого скана")
                    
                    # Store original points for validation
                    original_msg_points = msg_points.copy() if msg_idx == 0 else None
                    
                    # Apply transformation
                    msg_points = apply_transform_to_points(msg_points, transform_matrix)
                    
                    if msg_idx == 0:
                        print(f"      ✅ Трансформация применена к {len(msg_points)} точкам")
                        # Show transformation result for first few points
                        for i in range(min(3, len(msg_points))):
                            print(f"         Point {i} after transform: ({msg_points[i, 0]:.6f}, {msg_points[i, 1]:.6f}, {msg_points[i, 2]:.6f})")
                        
                        # Validate transformation on first message
                        if original_msg_points is not None:
                            validate_coordinate_systems(
                                original_msg_points, 
                                msg_points, 
                                f"{transform_mode} transformation"
                            )
                
                # Add transformed points to global lists
                x_list.extend(msg_points[:, 0])
                y_list.extend(msg_points[:, 1])
                z_list.extend(msg_points[:, 2])
            
            # Progress indicator
            if (msg_idx + 1) % max(1, len(message_points_data) // 20) == 0 or msg_idx < 3:
                progress = ((msg_idx + 1) / len(message_points_data)) * 100
                elapsed = time.time() - start_time
                print(f"   📊 [{progress:5.1f}%] Processed message {msg_idx + 1}/{len(message_points_data)} - {len(msg_points)} points")

        # Close the bag file
        bag.close()

        # Convert lists to numpy arrays
        print(f"\n🔢 CONVERTING TO NUMPY ARRAYS...")
        conversion_start = time.time()
        
        print("   🔄 Converting X coordinates...")
        x_array = np.array(x_list, dtype=np.float64)
        print(f"   ✅ X coordinates converted ({len(x_array):,} points)")
        print(f"   🔍 Debug - X array stats: min={np.min(x_array):.6f}, max={np.max(x_array):.6f}")
        
        print("   🔄 Converting Y coordinates...")
        y_array = np.array(y_list, dtype=np.float64)
        print(f"   ✅ Y coordinates converted ({len(y_array):,} points)")
        print(f"   🔍 Debug - Y array stats: min={np.min(y_array):.6f}, max={np.max(y_array):.6f}")
        
        print("   🔄 Converting Z coordinates...")
        z_array = np.array(z_list, dtype=np.float64)
        print(f"   ✅ Z coordinates converted ({len(z_array):,} points)")
        print(f"   🔍 Debug - Z array stats: min={np.min(z_array):.6f}, max={np.max(z_array):.6f}")
        
        # Add debug info about original lists before conversion
        print(f"   🔍 Debug - Original list sizes: x={len(x_list)}, y={len(y_list)}, z={len(z_list)}")
        print(f"   🔍 Debug - First 3 points from lists:")
        for i in range(min(3, len(x_list))):
            print(f"      Point {i}: ({x_list[i]:.6f}, {y_list[i]:.6f}, {z_list[i]:.6f})")
        
        if has_intensity:
            print("   🔄 Converting intensity values...")
            intensity_array = np.array(intensity_list, dtype=np.float32)
            print(f"   ✅ Intensity values converted ({len(intensity_array):,} points)")
            
        if has_gps_time:
            print("   🔄 Converting GPS time values...")
            gps_time_array = np.array(gps_time_list, dtype=np.float64)
            print(f"   ✅ GPS time values converted ({len(gps_time_array):,} points)")

        conversion_time = time.time() - conversion_start
        print(f"   ⏱️  Array conversion completed in {conversion_time:.2f} seconds")
        print(f"   💾 Memory usage: ~{(len(x_array) * 3 * 8) / 1024 / 1024:.1f} MB for coordinates")
        
        # Data quality analysis
        print(f"\n🔍 DATA QUALITY ANALYSIS:")
        print("-" * 50)
        
        # Coordinate statistics
        print(f"📍 Coordinate ranges:")
        print(f"   • X: {np.min(x_array):12.6f} to {np.max(x_array):12.6f} (range: {np.max(x_array) - np.min(x_array):10.6f})")
        print(f"   • Y: {np.min(y_array):12.6f} to {np.max(y_array):12.6f} (range: {np.max(y_array) - np.min(y_array):10.6f})")
        print(f"   • Z: {np.min(z_array):12.6f} to {np.max(z_array):12.6f} (range: {np.max(z_array) - np.min(z_array):10.6f})")
        
        # Check for valid coordinates
        nan_x = np.isnan(x_array).sum()
        nan_y = np.isnan(y_array).sum()
        nan_z = np.isnan(z_array).sum()
        inf_x = np.isinf(x_array).sum()
        inf_y = np.isinf(y_array).sum()
        inf_z = np.isinf(z_array).sum()
        
        print(f"\n🧪 Data integrity:")
        print(f"   • NaN values - X: {nan_x}, Y: {nan_y}, Z: {nan_z}")
        print(f"   • Inf values - X: {inf_x}, Y: {inf_y}, Z: {inf_z}")
        print(f"   • Zero values - X: {np.sum(x_array == 0)}, Y: {np.sum(y_array == 0)}, Z: {np.sum(z_array == 0)}")
        print(f"   • Total points before filtering: {len(x_array):,}")
        
        # More comprehensive filtering
        valid_mask = ~(np.isnan(x_array) | np.isnan(y_array) | np.isnan(z_array) |
                      np.isinf(x_array) | np.isinf(y_array) | np.isinf(z_array))
        
        # Additional check for extremely small values that might be precision errors
        extremely_small_threshold = 1e-10
        too_small_x = np.abs(x_array) < extremely_small_threshold
        too_small_y = np.abs(y_array) < extremely_small_threshold  
        too_small_z = np.abs(z_array) < extremely_small_threshold
        
        print(f"   • Extremely small values - X: {np.sum(too_small_x)}, Y: {np.sum(too_small_y)}, Z: {np.sum(too_small_z)}")
        
        # Check for points at origin (might be invalid)
        origin_points = (np.abs(x_array) < 1e-6) & (np.abs(y_array) < 1e-6) & (np.abs(z_array) < 1e-6)
        print(f"   • Points near origin (0,0,0): {np.sum(origin_points)}")
        
        if nan_x + nan_y + nan_z + inf_x + inf_y + inf_z > 0:
            print("⚠️  WARNING: Invalid values detected, filtering...")
            x_array = x_array[valid_mask]
            y_array = y_array[valid_mask]
            z_array = z_array[valid_mask]
            if has_intensity:
                intensity_array = intensity_array[valid_mask]
            if has_gps_time:
                gps_time_array = gps_time_array[valid_mask]
            print(f"✅ Valid points after filtering: {len(x_array):,}")
        else:
            print("✅ All coordinate values are valid")
        
        if len(x_array) == 0:
            print("❌ ERROR: No valid points remaining after filtering")
            return

        print(f"\n📁 CREATING LAS FILE...")
        print("-" * 50)
        
        # Extract the base filename from the bag file path
        base_filename = os.path.splitext(os.path.basename(bag_file))[0]

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📂 Created output directory: {output_dir}")

        # Create LAS file (uncompressed)
        output_file = os.path.join(output_dir, base_filename + ".las")
        print(f"🎯 Output file: {output_file}")
        
        # Choose appropriate point format based on available fields (NO RGB)
        # Point format 0: XYZ only
        # Point format 1: XYZ + GPS time + intensity
        # Point format 4: XYZ + GPS time (no intensity, no RGB)
        # Point format 6: XYZ + GPS time (LAS 1.4, no intensity, no RGB)
        if has_gps_time and has_intensity:
            point_format = 1  # GPS time + intensity (no RGB)
        elif has_gps_time:
            point_format = 6  # GPS time only (LAS 1.4, no RGB)
        elif has_intensity:
            point_format = 0  # Basic format with intensity handled as extra dimension
        else:
            point_format = 0  # Basic format
        
        print(f"🔧 Using point format: {point_format}")
        
        # Display format capabilities
        format_capabilities = {
            0: "XYZ",
            1: "XYZ + GPS time + intensity",
            4: "XYZ + GPS time",
            6: "XYZ + GPS time (LAS 1.4)"
        }
        print(f"   📋 Format {point_format} supports: {format_capabilities.get(point_format, 'Unknown')}")
        
        out_las = laspy.create(file_version='1.4', point_format=point_format)
        
        print(f"⚙️  Setting coordinate data...")
        # Set X, Y, Z coordinates
        out_las.x = x_array
        out_las.y = y_array
        out_las.z = z_array
        
        # Set intensity if available and supported by format
        if has_intensity:
            if point_format in [1]:  # Only format 1 officially supports intensity
                print(f"⚙️  Processing intensity data...")
                # Keep intensity in original format
                max_intensity = np.max(intensity_array)
                min_intensity = np.min(intensity_array)
                print(f"   • Original intensity range: {min_intensity:.3f} to {max_intensity:.3f}")
                print(f"   • Unique intensity values: {len(np.unique(intensity_array)):,}")
                
                # Use intensity as-is without scaling
                out_las.intensity = intensity_array.astype(np.uint16)
                print(f"   • Intensity used as-is (original values)")
                print(f"   ✅ Intensity data added successfully")
            else:
                print(f"   ⚠️  WARNING: Point format {point_format} doesn't support intensity field")
                print(f"   ℹ️  Intensity data will be lost in this format")
        
        # Set GPS time if available
        if has_gps_time:
            print(f"⚙️  Processing GPS time data...")
            print(f"   • GPS time array length: {len(gps_time_array):,}")
            print(f"   • GPS time data type: {gps_time_array.dtype}")
            print(f"   • GPS time range: {np.min(gps_time_array):.6f} to {np.max(gps_time_array):.6f}")
            print(f"   • Unique GPS time values: {len(np.unique(gps_time_array)):,}")
            
            # Alternative: Create sequential time for better visualization
            if use_ros_time:
                print(f"   🎨 Creating sequential time for better visualization...")
                # Create linearly increasing time across all points
                total_duration = np.max(gps_time_array) - np.min(gps_time_array)
                if total_duration > 0:
                    # Create smooth time progression
                    sequential_time = np.linspace(
                        np.min(gps_time_array), 
                        np.max(gps_time_array), 
                        len(gps_time_array)
                    )
                    gps_time_array = sequential_time
                    print(f"   • Sequential time created: {np.min(gps_time_array):.6f} to {np.max(gps_time_array):.6f}")
                    print(f"   • Time step: {(np.max(gps_time_array) - np.min(gps_time_array)) / len(gps_time_array):.6f} s")
                else:
                    # If all timestamps are the same, create artificial progression
                    base_time = gps_time_array[0]
                    duration = len(points_per_message) * 0.1  # 0.1 seconds per message
                    sequential_time = np.linspace(base_time, base_time + duration, len(gps_time_array))
                    gps_time_array = sequential_time
                    print(f"   • Artificial time progression created over {duration:.1f} seconds")
            
            # More detailed time analysis
            time_diffs = np.diff(gps_time_array)
            non_zero_diffs = time_diffs[time_diffs > 0]
            if len(non_zero_diffs) > 0:
                print(f"   • Min time difference: {np.min(non_zero_diffs):.6f} s")
                print(f"   • Max time difference: {np.max(non_zero_diffs):.6f} s")
                print(f"   • Average time difference: {np.mean(non_zero_diffs):.6f} s")
                print(f"   • Median time difference: {np.median(non_zero_diffs):.6f} s")
            
            # Check for time progression
            monotonic_increasing = np.all(np.diff(gps_time_array) >= 0)
            print(f"   • Time is monotonically increasing: {monotonic_increasing}")
            if not monotonic_increasing:
                print("   ⚠️  WARNING: Time values are not monotonically increasing")
                print("   🔄 Sorting points by time for proper visualization...")
                # Sort all arrays by time
                sort_indices = np.argsort(gps_time_array)
                gps_time_array = gps_time_array[sort_indices]
                x_array = x_array[sort_indices]
                y_array = y_array[sort_indices]
                z_array = z_array[sort_indices]
                if has_intensity:
                    intensity_array = intensity_array[sort_indices]
                print("   ✅ Points sorted by timestamp")
            
            print(f"   • First 10 GPS time values: {gps_time_array[:10]}")
            print(f"   • Last 10 GPS time values: {gps_time_array[-10:]}")
            
            # Analyze GPS time characteristics
            time_diff = np.max(gps_time_array) - np.min(gps_time_array)
            print(f"   • Total time span: {time_diff:.6f} seconds ({time_diff/60:.2f} minutes)")
            
            # Visualization recommendations
            unique_times = len(np.unique(gps_time_array))
            if unique_times == len(gps_time_array):
                print("   🎨 Perfect for temporal visualization - each point has unique time")
            elif unique_times > len(gps_time_array) * 0.8:
                print("   🎨 Good for temporal visualization - most points have unique times")
            elif unique_times > 10:
                print("   🎨 Acceptable for temporal visualization - points grouped by scan time")
            else:
                print("   ⚠️  Limited temporal visualization - few unique timestamps")

        # Set GPS time if available
        if has_gps_time:
            print(f"⚙️  Processing GPS time data...")
            print(f"   • GPS time array length: {len(gps_time_array):,}")
            print(f"   • GPS time data type: {gps_time_array.dtype}")
            print(f"   • GPS time range: {np.min(gps_time_array):.6f} to {np.max(gps_time_array):.6f}")
            print(f"   • Unique GPS time values: {len(np.unique(gps_time_array)):,}")
            
            # More detailed time analysis
            time_diffs = np.diff(gps_time_array)
            non_zero_diffs = time_diffs[time_diffs > 0]
            if len(non_zero_diffs) > 0:
                print(f"   • Min time difference: {np.min(non_zero_diffs):.6f} s")
                print(f"   • Max time difference: {np.max(non_zero_diffs):.6f} s")
                print(f"   • Average time difference: {np.mean(non_zero_diffs):.6f} s")
                print(f"   • Median time difference: {np.median(non_zero_diffs):.6f} s")
            
            # Check for time progression
            monotonic_increasing = np.all(np.diff(gps_time_array) >= 0)
            print(f"   • Time is monotonically increasing: {monotonic_increasing}")
            if not monotonic_increasing:
                print("   ⚠️  WARNING: Time values are not monotonically increasing")
            
            print(f"   • First 10 GPS time values: {gps_time_array[:10]}")
            print(f"   • Last 10 GPS time values: {gps_time_array[-10:]}")
            
            # Analyze GPS time characteristics
            time_diff = np.max(gps_time_array) - np.min(gps_time_array)
            print(f"   • Total time span: {time_diff:.6f} seconds ({time_diff/60:.2f} minutes)")
            
            # Check time distribution across messages
            if use_ros_time and len(points_per_message) > 1:
                estimated_duration = len(points_per_message) * 0.1  # assuming 10Hz
                print(f"   • Estimated scan duration: {estimated_duration:.1f} seconds")
                print(f"   • Time span vs estimated: {time_diff:.1f}s vs {estimated_duration:.1f}s")
            
            # Check if GPS time values are reasonable and normalize if needed
            if np.all(gps_time_array == 0):
                print("   ⚠️  WARNING: All GPS time values are zero")
            elif np.max(gps_time_array) < 1:
                print("   ⚠️  WARNING: GPS time values seem to be relative (too small)")
            elif np.min(gps_time_array) > 100:
                # Always normalize large GPS time values for CloudCompare compatibility
                print("   ℹ️  GPS time values are large - normalizing for CloudCompare compatibility")
                min_gps_time = np.min(gps_time_array)
                max_gps_time_orig = np.max(gps_time_array)
                gps_time_array = gps_time_array - min_gps_time
                print(f"   🔄 Normalizing GPS time to relative values starting from 0...")
                print(f"   • Original range: {min_gps_time:.6f} to {max_gps_time_orig:.6f}")
                print(f"   • Normalized range: 0.0 to {np.max(gps_time_array):.6f}")
                print(f"   • Duration: {np.max(gps_time_array):.2f} seconds ({np.max(gps_time_array)/60:.2f} minutes)")
                print(f"   • This allows proper time-based filtering in CloudCompare")
            else:
                print(f"   ℹ️  GPS time values are in reasonable range (0-100)")
                print(f"   • Range: {np.min(gps_time_array):.6f} to {np.max(gps_time_array):.6f}")
            
            try:
                # Ensure GPS time is in the correct format for LAS
                if point_format in [1, 4, 6]:
                    out_las.gps_time = gps_time_array
                    print(f"   ✅ GPS time data assigned to LAS file")
                    
                    # Verify the assignment worked
                    if hasattr(out_las, 'gps_time') and out_las.gps_time is not None:
                        actual_min = np.min(out_las.gps_time)
                        actual_max = np.max(out_las.gps_time)
                        actual_unique = len(np.unique(out_las.gps_time))
                        print(f"   ✅ Verified GPS time in LAS: {actual_min:.6f} to {actual_max:.6f}")
                        print(f"   ✅ Unique time values in LAS: {actual_unique:,}")
                        print("   ✅ GPS time successfully added to LAS file")
                        
                        # Check if each point has unique time
                        if actual_unique == len(gps_time_array):
                            print("   ✅ Each point has unique timestamp")
                        elif actual_unique < len(gps_time_array) * 0.5:
                            print("   ⚠️  WARNING: Many points share the same timestamp")
                        else:
                            print("   ℹ️  Some points share timestamps (normal for synchronized scans)")
                    else:
                        print("   ❌ ERROR: GPS time field is None or doesn't exist in LAS")
                else:
                    print(f"   ⚠️  WARNING: Point format {point_format} doesn't support GPS time")
            except Exception as e:
                print(f"   ❌ ERROR setting GPS time: {e}")
                import traceback
                traceback.print_exc()

        print(f"⚙️  Setting LAS header parameters...")
        # Set proper header values
        out_las.header.offset = [np.min(x_array), np.min(y_array), np.min(z_array)]
        out_las.header.scale = [0.001, 0.001, 0.001]  # 1mm precision
        print(f"   • Offset: [{out_las.header.offset[0]:.6f}, {out_las.header.offset[1]:.6f}, {out_las.header.offset[2]:.6f}]")
        print(f"   • Scale: [{out_las.header.scale[0]}, {out_las.header.scale[1]}, {out_las.header.scale[2]}]")
        
        # No RGB values - skip RGB assignment entirely
        print(f"   ℹ️  No RGB data (point cloud contains no color information)")
        
        # Save the LAS file
        print(f"\n💾 WRITING LAS FILE...")
        write_start = time.time()
        out_las.write(output_file)
        write_time = time.time() - write_start
        print(f"   ⏱️  File write completed in {write_time:.2f} seconds")

        # Create .POS file from odometry data
        if odometry_topic:
            create_pos_file(bag_file, output_dir, odometry_topic)
        else:
            print("\n⚠️  .POS файл не создан - топик одометрии не выбран")

        # Verify file was created and provide detailed summary
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n🎉 SUCCESS! LAS FILE CREATED")
            print("=" * 50)
            print(f"📁 File: {output_file}")
            print(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"🔢 Points: {len(x_array):,}")
            print(f"📏 Point format: {point_format}")
            print(f"🗂️  LAS version: 1.4")
            print(f"🔧 Transform mode: {transform_mode}")
            
            if transform_mode != "none":
                print(f"   🌍 Point cloud transformed using odometry data")
                if transform_mode == "global":
                    print(f"   📍 Coordinates in global odometry frame")
                    if enable_slam and slam_metrics:
                        print(f"   🤖 SLAM optimization applied:")
                        print(f"      • Loop closures found: {slam_metrics.get('loop_closures_found', 0)}")
                        print(f"      • Average position correction: {slam_metrics.get('average_position_change', 0):.3f} m")
                        if slam_metrics.get('loop_closures_found', 0) > 0:
                            print(f"      • Drift reduction: {slam_metrics.get('original_drift', 0):.3f} → {slam_metrics.get('optimized_drift', 0):.3f} m")
                        
                        # Create trajectory visualization if SLAM was applied
                        try:
                            print(f"\n📊 Создание визуализации траектории SLAM...")
                            # Get original positions from loaded odometry
                            if 'odom_positions_original' in locals() and slam_metrics:
                                plot_file = visualize_trajectory_comparison(
                                    odom_positions_original, odom_positions, slam_metrics,
                                    output_dir, base_filename
                                )
                                if plot_file:
                                    print(f"   ✅ График сохранен: {plot_file}")
                            else:
                                print(f"   ⚠️  Визуализация недоступна: отсутствуют исходные данные траектории")
                        except Exception as viz_error:
                            print(f"   ⚠️  Ошибка создания визуализации: {viz_error}")
                elif transform_mode == "local":
                    print(f"   📍 Coordinates relative to first scan position")
            else:
                print(f"   📡 Original sensor coordinates (no transformation)")
                
            # Check for .POS file
            base_filename = os.path.splitext(os.path.basename(bag_file))[0]
            pos_file = os.path.join(output_dir, base_filename + ".pos")
            if os.path.exists(pos_file):
                pos_size = os.path.getsize(pos_file)
                print(f"🧭 POS file: {pos_file}")
                print(f"📊 POS size: {pos_size:,} bytes")
            
            # Detailed field verification
            try:
                # Re-read the file to verify it's valid
                verify_las = laspy.read(output_file)
                print(f"\n✅ FILE VERIFICATION:")
                print(f"   • Points in file: {len(verify_las.points):,}")
                print(f"   • Coordinate ranges verified:")
                print(f"     - X: {np.min(verify_las.x):.6f} to {np.max(verify_las.x):.6f}")
                print(f"     - Y: {np.min(verify_las.y):.6f} to {np.max(verify_las.y):.6f}")
                print(f"     - Z: {np.min(verify_las.z):.6f} to {np.max(verify_las.z):.6f}")
                
                if has_intensity and hasattr(verify_las, 'intensity'):
                    print(f"   • Intensity verified: {np.min(verify_las.intensity)} - {np.max(verify_las.intensity)}")
                    print(f"⚡ Intensity: ✅ Range {np.min(intensity_array):.3f} - {np.max(intensity_array):.3f}")
                
                if has_gps_time and hasattr(verify_las, 'gps_time'):
                    print(f"   • GPS time verified: {np.min(verify_las.gps_time):.6f} - {np.max(verify_las.gps_time):.6f}")
                    print(f"   • GPS time unique values: {len(np.unique(verify_las.gps_time)):,}")
                    print(f"⏰ GPS time: ✅ Range {np.min(gps_time_array):.6f} - {np.max(gps_time_array):.6f}")
                    
                    # Check temporal distribution
                    time_span = np.max(verify_las.gps_time) - np.min(verify_las.gps_time)
                    if time_span > 0:
                        points_per_second = len(verify_las.points) / time_span
                        print(f"   • Temporal density: {points_per_second:.0f} points/second")
                        print(f"   🎨 Ready for temporal visualization in CloudCompare!")
                
                print(f"   ✅ LAS file is valid and ready for use")
                
            except Exception as e:
                print(f"   ⚠️  Warning: Could not verify file: {e}")
            
        else:
            print("❌ ERROR: LAS file was not created")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

def analyze_bag_topics(bag_file):
    """
    Analyze and display all topics in the bag file with detailed information.
    
    Parameters:
        bag_file (str): Path to the ROS bag file
        
    Returns:
        dict: Dictionary with topic analysis results
    """
    print(f"\n🔍 ПОЛНЫЙ АНАЛИЗ ТОПИКОВ В BAG ФАЙЛЕ")
    print("=" * 80)
    print(f"📂 Файл: {os.path.basename(bag_file)}")
    
    try:
        with rosbag.Bag(bag_file, 'r') as bag:
            # Get bag info
            bag_info = bag.get_type_and_topic_info()
            total_topics = len(bag_info.topics)
            total_messages = bag.get_message_count()
            
            # Get bag duration
            start_time = bag.get_start_time()
            end_time = bag.get_end_time()
            duration = end_time - start_time if start_time and end_time else 0
            
            print(f"📊 Общая информация:")
            print(f"   • Всего топиков: {total_topics}")
            print(f"   • Всего сообщений: {total_messages:,}")
            print(f"   • Длительность: {duration:.2f} секунд ({duration/60:.2f} минут)")
            if duration > 0:
                print(f"   • Средняя частота: {total_messages/duration:.1f} сообщений/сек")
            print(f"   • Время начала: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)) if start_time else 'unknown'}")
            print(f"   • Время окончания: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)) if end_time else 'unknown'}")
            
            # Categorize topics by type
            topic_categories = {
                'sensor_msgs/PointCloud2': [],
                'nav_msgs/Odometry': [],
                'sensor_msgs/Image': [],
                'sensor_msgs/CompressedImage': [],
                'sensor_msgs/Imu': [],
                'geometry_msgs/Twist': [],
                'tf/tfMessage': [],
                'tf2_msgs/TFMessage': [],
                'other': []
            }
            
            # Sort topics by name for consistent display
            sorted_topics = sorted(bag_info.topics.items())
            
            print(f"\n📋 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ТОПИКАМ:")
            print("-" * 80)
            print(f"{'№':>3} | {'Топик':^40} | {'Тип':^25} | {'Сообщ.':>8} | {'Частота':>8}")
            print("-" * 80)
            
            for i, (topic_name, topic_info) in enumerate(sorted_topics, 1):
                msg_type = topic_info.msg_type
                msg_count = topic_info.message_count
                frequency = topic_info.frequency
                
                # Categorize topic
                if msg_type in topic_categories:
                    topic_categories[msg_type].append(topic_name)
                else:
                    topic_categories['other'].append(topic_name)
                
                # Format frequency with None check
                freq_str = f"{frequency:.1f} Hz" if frequency is not None and frequency > 0 else "0 Hz"
                
                # Truncate long topic names for display
                display_topic = topic_name[:38] + ".." if len(topic_name) > 40 else topic_name
                display_type = msg_type.split('/')[-1][:23] + ".." if len(msg_type) > 25 else msg_type.split('/')[-1]
                
                print(f"{i:3d} | {display_topic:<40} | {display_type:<25} | {msg_count:8,} | {freq_str:>8}")
            
            print("-" * 80)
            
            # Show categorized summary
            print(f"\n🎯 КАТЕГОРИИ ТОПИКОВ:")
            print("-" * 50)
            
            # PointCloud2 topics
            if topic_categories['sensor_msgs/PointCloud2']:
                print(f"📡 PointCloud2 топики ({len(topic_categories['sensor_msgs/PointCloud2'])}):")
                for topic in topic_categories['sensor_msgs/PointCloud2']:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    print(f"   • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # Odometry topics
            if topic_categories['nav_msgs/Odometry']:
                print(f"🧭 Odometry топики ({len(topic_categories['nav_msgs/Odometry'])}):")
                for topic in topic_categories['nav_msgs/Odometry']:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    print(f"   • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # Image topics
            image_topics = topic_categories['sensor_msgs/Image'] + topic_categories['sensor_msgs/CompressedImage']
            if image_topics:
                print(f"📷 Image топики ({len(image_topics)}):")
                for topic in image_topics:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    msg_type = bag_info.topics[topic].msg_type.split('/')[-1]
                    print(f"   • {topic} ({count:,} сообщений, {freq_display}, {msg_type})")
                print()
            
            # IMU topics
            if topic_categories['sensor_msgs/Imu']:
                print(f"🎯 IMU топики ({len(topic_categories['sensor_msgs/Imu'])}):")
                for topic in topic_categories['sensor_msgs/Imu']:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    print(f"   • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # TF topics
            tf_topics = topic_categories['tf/tfMessage'] + topic_categories['tf2_msgs/TFMessage']
            if tf_topics:
                print(f"🔗 Transform топики ({len(tf_topics)}):")
                for topic in tf_topics:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    print(f"   • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # Control topics
            if topic_categories['geometry_msgs/Twist']:
                print(f"🎮 Control топики ({len(topic_categories['geometry_msgs/Twist'])}):")
                for topic in topic_categories['geometry_msgs/Twist']:
                    count = bag_info.topics[topic].message_count
                    freq = bag_info.topics[topic].frequency
                    freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                    print(f"   • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # Other topics
            if topic_categories['other']:
                print(f"📦 Другие топики ({len(topic_categories['other'])}):")
                # Group by message type
                other_by_type = {}
                for topic in topic_categories['other']:
                    msg_type = bag_info.topics[topic].msg_type
                    if msg_type not in other_by_type:
                        other_by_type[msg_type] = []
                    other_by_type[msg_type].append(topic)
                
                for msg_type, topics in sorted(other_by_type.items()):
                    print(f"   📄 {msg_type}:")
                    for topic in topics:
                        count = bag_info.topics[topic].message_count
                        freq = bag_info.topics[topic].frequency
                        freq_display = f"{freq:.1f} Hz" if freq is not None and freq > 0 else "0 Hz"
                        print(f"      • {topic} ({count:,} сообщений, {freq_display})")
                print()
            
            # Summary statistics
            pointcloud_count = len(topic_categories['sensor_msgs/PointCloud2'])
            odometry_count = len(topic_categories['nav_msgs/Odometry'])
            
            print(f"✅ АНАЛИЗ ЗАВЕРШЕН:")
            print(f"   • PointCloud2 топиков: {pointcloud_count}")
            print(f"   • Odometry топиков: {odometry_count}")
            print(f"   • Других топиков: {total_topics - pointcloud_count - odometry_count}")
            
            if pointcloud_count == 0:
                print("   ⚠️  WARNING: Нет PointCloud2 топиков для конвертации!")
            if odometry_count == 0:
                print("   ⚠️  WARNING: Нет Odometry топиков для создания .POS файла!")
            
            return {
                'total_topics': total_topics,
                'total_messages': total_messages,
                'duration': duration,
                'pointcloud2_topics': topic_categories['sensor_msgs/PointCloud2'],
                'odometry_topics': topic_categories['nav_msgs/Odometry'],
                'topics_info': bag_info.topics
            }
            
    except Exception as e:
        print(f"❌ Ошибка анализа bag файла: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_user_choice():
    """
    Функция для получения выбора пользователя: файл или директория
    
    Returns:
        tuple: (mode, path) где mode - 'file' или 'directory', path - путь к файлу/директории
    """
    print("\n🎯 ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:")
    print("=" * 50)
    print("1. 📁 Обработать всю директорию (.bag файлы)")
    print("2. 📄 Обработать конкретный файл (.bag)")
    print("3. ❌ Выход")
    
    while True:
        try:
            choice = input("\nВведите номер (1-3): ").strip()
            
            if choice == "1":
                # Режим директории
                directory = input("📂 Введите путь к директории (или Enter для текущей): ").strip()
                if not directory:
                    directory = os.path.dirname(os.path.abspath(__file__))
                
                if not os.path.isdir(directory):
                    print(f"❌ Директория не найдена: {directory}")
                    continue
                
                return "directory", directory
                
            elif choice == "2":
                # Режим отдельного файла
                file_path = input("📄 Введите полный путь к .bag файлу: ").strip()
                
                if not file_path:
                    print("❌ Путь не может быть пустым")
                    continue
                    
                if not os.path.isfile(file_path):
                    print(f"❌ Файл не найден: {file_path}")
                    continue
                    
                if not file_path.endswith(".bag"):
                    print("❌ Файл должен иметь расширение .bag")
                    continue
                
                return "file", file_path
                
            elif choice == "3":
                print("👋 Выход из программы")
                exit(0)
                
            else:
                print("❌ Неверный выбор. Введите 1, 2 или 3")
                
        except KeyboardInterrupt:
            print("\n👋 Программа прервана пользователем")
            exit(0)
        except Exception as e:
            print(f"❌ Ошибка ввода: {e}")

def process_single_file(bag_file_path, output_dir=None, selected_topic=None, transform_mode=None, enable_slam=None):
    """
    Обработка одного .bag файла
    
    Parameters:
        bag_file_path (str): Путь к .bag файлу
        output_dir (str): Директория для сохранения (по умолчанию - рядом с исходным файлом)
        selected_topic (str): Выбранный топик (если None, будет предложен выбор)
        transform_mode (str): Режим трансформации (None для выбора пользователем)
        enable_slam (bool): Включить SLAM оптимизацию (None для выбора пользователем)
    """
    if output_dir is None:
        # Использовать директорию исходного файла
        output_dir = os.path.dirname(bag_file_path)
    
    print(f"🎯 ОБРАБОТКА ОТДЕЛЬНОГО ФАЙЛА")
    print("=" * 60)
    print(f"📂 Исходный файл: {bag_file_path}")
    print(f"📁 Директория вывода: {output_dir}")
    
    # Проверить размер файла
    file_size = os.path.getsize(bag_file_path)
    print(f"📊 Размер файла: {file_size:,} байт ({file_size/1024/1024:.1f} МБ)")
    
    try:
        start_time = time.time()
        convert_bag_to_laz(bag_file_path, output_dir, selected_topic, transform_mode, enable_slam)
        elapsed_time = time.time() - start_time
        
        print(f"\n🎉 ФАЙЛ УСПЕШНО ОБРАБОТАН!")
        print(f"⏱️  Время обработки: {int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}")
        
        # Показать результирующие файлы
        base_filename = os.path.splitext(os.path.basename(bag_file_path))[0]
        output_file = os.path.join(output_dir, base_filename + ".las")
        
        if os.path.exists(output_file):
            output_size = os.path.getsize(output_file)
            print(f"📁 Создан файл: {output_file}")
            print(f"📊 Размер LAS: {output_size:,} байт ({output_size/1024/1024:.1f} МБ)")
            print(f"📈 Коэффициент сжатия: {file_size/output_size:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА при обработке файла: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_directory(bag_directory, output_dir, selected_topic=None, transform_mode=None, enable_slam=None):
    """
    Обработка всех .bag файлов в директории
    
    Parameters:
        bag_directory (str): Директория с .bag файлами
        output_dir (str): Директория для сохранения результатов
        selected_topic (str): Выбранный топик для всех файлов (если None, будет предложен выбор для каждого)
        transform_mode (str): Режим трансформации для всех файлов (None для выбора пользователем)
        enable_slam (bool): Включить SLAM оптимизацию для всех файлов (None для выбора пользователем)
    """
    print(f"🎯 ОБРАБОТКА ДИРЕКТОРИИ")
    print("=" * 60)
    print(f"📂 Входная директория: {bag_directory}")
    print(f"📁 Выходная директория: {output_dir}")

    # Сканирование .bag файлов
    bag_files = [f for f in os.listdir(bag_directory) if f.endswith(".bag")]
    print(f"🔍 Найдено {len(bag_files)} .bag файл(ов)")
    
    if not bag_files:
        print(f"❌ .bag файлы не найдены в директории: {bag_directory}")
        return False
    
    # Список всех найденных файлов
    total_size = 0
    for i, bag_file in enumerate(bag_files, 1):
        bag_path = os.path.join(bag_directory, bag_file)
        size = os.path.getsize(bag_path)
        total_size += size
        print(f"   {i:2d}. {bag_file} ({size/1024/1024:.1f} МБ)")
    
    print(f"📊 Общий размер: {total_size/1024/1024:.1f} МБ")
    
    # Если топик не выбран, предложить выбрать общий топик для всех файлов
    use_same_topic_for_all = False
    if selected_topic is None and len(bag_files) > 1:
        choice = input(f"\n❓ Использовать один топик для всех файлов? (y/n): ").strip().lower()
        if choice in ['y', 'yes', 'д', 'да']:
            print("🔍 Анализ первого файла для выбора топика...")
            first_bag_path = os.path.join(bag_directory, bag_files[0])
            selected_topic = choose_pointcloud2_topic(first_bag_path)
            if selected_topic:
                use_same_topic_for_all = True
                print(f"✅ Будет использован топик '{selected_topic}' для всех файлов")
            else:
                print("❌ Топик не выбран, будет предложен выбор для каждого файла")
    
    # Подтверждение обработки
    confirm = input(f"\n❓ Обработать все {len(bag_files)} файлов? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', 'д', 'да']:
        print("❌ Обработка отменена")
        return False

    # Обработка каждого файла
    success_count = 0
    total_start_time = time.time()
    
    for i, bag_file in enumerate(bag_files, 1):
        try:
            bag_file_path = os.path.join(bag_directory, bag_file)
            file_progress = (i / len(bag_files)) * 100
            
            print(f"\n🔄 [{file_progress:5.1f}%] Обработка файла {i}/{len(bag_files)}: {bag_file}")
            print("=" * 60)
            
            # Использовать выбранный топик или дать возможность выбрать для каждого файла
            topic_for_this_file = selected_topic if use_same_topic_for_all else None
            
            file_start_time = time.time()
            convert_bag_to_laz(bag_file_path, output_dir, topic_for_this_file, transform_mode, enable_slam)
            file_elapsed = time.time() - file_start_time
            
            print(f"\n✅ Файл обработан за {int(file_elapsed//60):02d}:{int(file_elapsed%60):02d}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка обработки {bag_file}: {e}")
    
    total_elapsed = time.time() - total_start_time
    print(f"\n🏁 ОБРАБОТКА ДИРЕКТОРИИ ЗАВЕРШЕНА!")
    print("=" * 80)
    print(f"⏱️  Общее время: {int(total_elapsed//60):02d}:{int(total_elapsed%60):02d}")
    print(f"✅ Успешно обработано: {success_count}/{len(bag_files)} файлов")
    
    if success_count < len(bag_files):
        print(f"❌ Ошибок: {len(bag_files) - success_count} файлов")
    
    if success_count > 0:
        avg_time_per_file = total_elapsed / success_count
        print(f"📊 Среднее время на файл: {avg_time_per_file:.1f} секунд")
    
    return success_count > 0

if __name__ == "__main__":
    import time  # Add time import for progress tracking
    
    print("🚀 КОНВЕРТЕР ROS BAG В LAS")
    print("=" * 80)
    print("Версия 2.0 - Поддержка выбора файлов и директорий")
    
    try:
        # Получить выбор пользователя
        mode, path = get_user_choice()
        
        if mode == "file":
            # Обработка отдельного файла
            output_dir = input(f"\n📁 Директория для сохранения (Enter для '{os.path.dirname(path)}'): ").strip()
            if not output_dir:
                output_dir = os.path.dirname(path)
            
            # Создать выходную директорию если не существует
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"📂 Создана директория: {output_dir}")
            
            success = process_single_file(path, output_dir)
            
        elif mode == "directory":
            # Обработка директории
            output_dir = input(f"\n📁 Директория для сохранения (Enter для '{path}'): ").strip()
            if not output_dir:
                output_dir = path
            
            # Создать выходную директорию если не существует
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"📂 Создана директория: {output_dir}")
            
            success = process_directory(path, output_dir)
        
        if success:
            print(f"\n🎉 ПРОГРАММА ЗАВЕРШЕНА УСПЕШНО!")
        else:
            print(f"\n❌ ПРОГРАММА ЗАВЕРШЕНА С ОШИБКАМИ")
            
    except KeyboardInterrupt:
        print(f"\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        # else:
        #     print(f"\n❌ ПРОГРАММА ЗАВЕРШЕНА С ОШИБКАМИ")
            
    except KeyboardInterrupt:
        print(f"\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

