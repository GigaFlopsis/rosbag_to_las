# Как удалить большой файл из Git

## ✅ Что было сделано

Файл `test.bag` (~1.1 ГБ) был случайно закоммичен и успешно удалён из истории git.

## 🔧 Шаги которые были выполнены:

### 1. Создание резервной копии
```bash
git branch backup-before-cleanup
```

### 2. Сброс коммитов (с сохранением изменений)
```bash
git reset --soft origin/main
```

Это откатило 3 коммита, но сохранило все изменения в индексе.

### 3. Удаление test.bag из индекса
```bash
git reset HEAD test.bag
```

### 4. Обновление .gitignore
Добавлены правила для исключения больших файлов:
```gitignore
# ROS bag files (слишком большие для git)
*.bag
test.bag

# Test output files
test_camera_positions.*
camera_debug_test.json
*.backup
```

### 5. Создание нового коммита (без test.bag)
```bash
git add .gitignore camera_frames_debug.py extract_camera_positions.py doc/
git commit -m "Добавлено ПО для извлечения позиций камеры из ROS bag"
```

### 6. Очистка старых объектов git
```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

Это удаляет test.bag из всех старых объектов git и сжимает репозиторий.

## 📊 Результат

**До:**
- История содержала test.bag (~1.1 ГБ)
- Размер .git: ~433 МБ
- 3 коммита с лишним файлом

**После:**
- test.bag только на диске (не отслеживается)
- История очищена
- Новый чистый коммит без большого файла
- Размер .git значительно меньше (после gc)

## 🚀 Следующие шаги

### Если изменения нужно отправить на сервер:

```bash
# Обычный push (история не переписана на сервере)
git push origin main

# ИЛИ если уже пушили старые коммиты - force push
# ⚠️ ВНИМАНИЕ: это перезапишет историю на сервере!
git push origin main --force
```

### Если что-то пошло не так:

```bash
# Вернуться к состоянию до изменений
git reset --hard backup-before-cleanup

# Удалить резервную ветку когда всё проверено
git branch -d backup-before-cleanup
```

## 💡 Рекомендации на будущее

### 1. Использовать .gitignore заранее
Добавьте в `.gitignore` ДО работы с большими файлами:
```gitignore
*.bag
*.rosbag
*.db3
*.mcap
```

### 2. Использовать Git LFS для больших файлов
Если нужно хранить большие файлы в git:
```bash
# Установить Git LFS
brew install git-lfs  # macOS
# или: apt install git-lfs  # Linux

# Инициализировать
git lfs install

# Отслеживать большие файлы
git lfs track "*.bag"
git add .gitattributes
```

### 3. Проверять перед коммитом
```bash
# Посмотреть что будет закоммичено
git status

# Посмотреть размеры файлов
git ls-files | xargs ls -lh

# Проверить размер коммита
git diff --cached --stat
```

## 🛠️ Альтернативные методы

### Метод 1: BFG Repo-Cleaner (рекомендуется для больших репозиториев)
```bash
# Установить BFG
brew install bfg  # macOS

# Удалить файл из истории
bfg --delete-files test.bag
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Метод 2: git filter-repo (современный способ)
```bash
# Установить
pip install git-filter-repo

# Удалить файл
git filter-repo --path test.bag --invert-paths

# Очистка
git gc --prune=now --aggressive
```

### Метод 3: Interactive Rebase (для недавних коммитов)
```bash
# Начать rebase
git rebase -i HEAD~3

# В редакторе изменить 'pick' на 'edit' для нужного коммита
# Удалить файл
git rm --cached test.bag
git commit --amend
git rebase --continue
```

## ⚠️ Важные замечания

1. **Force push переписывает историю** - координируйтесь с командой
2. **Локальная копия сохранена** - test.bag остался на диске
3. **Бэкап создан** - ветка `backup-before-cleanup` для отката
4. **Git gc может занять время** - особенно с `--aggressive`

## 📚 Полезные команды

```bash
# Найти большие файлы в истории
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -10

# Проверить размер репозитория
du -sh .git

# Посмотреть что игнорируется
git status --ignored

# Удалить файл из индекса но оставить на диске
git rm --cached <file>
```

---

**Создано:** 11 октября 2025  
**Проект:** rosbag_to_las
