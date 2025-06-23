# PAO Memory Trainer

A professional terminal-based training tool for memorizing PAO (Person-Action-Object) associations.

## Features

- 🧠 **Interactive Training**: Test your knowledge of number-to-PAO associations
- 📊 **Smart Statistics**: Track your accuracy for each number with persistent storage
- 🎯 **Adaptive Learning**: Focuses on your weakest associations
- 📖 **Browse Mode**: View all PAO associations with your current stats
- 🔄 **Session Tracking**: See your progress within each training session

## Usage

### Basic Training (Default)
```bash
python3 pao_trainer.py
```

### Browse All Associations
```bash
python3 pao_trainer.py --mode browse
```

### View Detailed Statistics
```bash
python3 pao_trainer.py --mode stats
```

## Training Commands

During training, you can use:
- **Enter**: Continue to next number
- **`quit`**: Exit training session
- **`stats`**: View detailed statistics

## How It Works

1. The script loads PAO associations from `pao_00_99.csv`
2. You'll be prompted with a random number (00-99)
3. Enter the Person, Action, and Object for that number
4. The script shows if you're correct and tracks your accuracy
5. Statistics are saved in `pao_stats.json` for persistent tracking

## Features

- **Adaptive Selection**: 30% chance to pick from your weakest numbers
- **Case-Insensitive**: Answers are checked regardless of capitalization
- **Persistent Stats**: Your progress is saved between sessions
- **Professional UI**: Clean terminal interface with emojis and clear formatting

Start training and master your PAO associations! 🚀 