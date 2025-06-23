#!/usr/bin/env python3
"""
PAO (Person-Action-Object) Memory Trainer
A professional terminal-based training tool for memorizing PAO associations.
"""

import csv
import random
import json
import os
import time
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import argparse


class PAOTrainer:
    def __init__(self, csv_file: str = "pao_00_99.csv", stats_file: str = "pao_stats.json"):
        self.csv_file = csv_file
        self.stats_file = stats_file
        self.pao_data: Dict[str, Dict[str, str]] = {}
        self.stats = self.load_stats()
        self.session_stats = {"correct": 0, "incorrect": 0, "total": 0}
        
    def load_pao_data(self) -> None:
        """Load PAO data from CSV file."""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    number = f"{int(row['Number']):02d}"  # Format as 2-digit string
                    self.pao_data[number] = {
                        'person': row['Person'],
                        'action': row['Action'],
                        'object': row['Object']
                    }
            print(f"✓ Loaded {len(self.pao_data)} PAO associations")
        except FileNotFoundError:
            print(f"Error: {self.csv_file} not found!")
            exit(1)
        except Exception as e:
            print(f"Error loading PAO data: {e}")
            exit(1)
    
    def load_stats(self) -> Dict:
        """Load training statistics from JSON file."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as file:
                    stats = json.load(file)
                    # Ensure all numbers have the required fields
                    for i in range(100):
                        number = f"{i:02d}"
                        if number not in stats:
                            stats[number] = {"correct": 0, "incorrect": 0, "last_tested": None}
                        elif "last_tested" not in stats[number]:
                            stats[number]["last_tested"] = None
                    return stats
            except (json.JSONDecodeError, IOError):
                pass
        
        # Initialize stats for all numbers 00-99
        return {f"{i:02d}": {"correct": 0, "incorrect": 0, "last_tested": None} for i in range(100)}
    
    def save_stats(self) -> None:
        """Save training statistics to JSON file."""
        try:
            with open(self.stats_file, 'w') as file:
                json.dump(self.stats, file, indent=2)
        except IOError as e:
            print(f"Warning: Could not save stats: {e}")
    
    def update_stats(self, number: str, correct: bool) -> None:
        """Update statistics for a number."""
        if correct:
            self.stats[number]["correct"] += 1
            self.session_stats["correct"] += 1
        else:
            self.stats[number]["incorrect"] += 1
            self.session_stats["incorrect"] += 1
        
        # Update last tested timestamp
        self.stats[number]["last_tested"] = datetime.now().isoformat()
        self.session_stats["total"] += 1
    
    def get_accuracy(self, number: str) -> float:
        """Get accuracy percentage for a specific number."""
        correct = self.stats[number]["correct"]
        incorrect = self.stats[number]["incorrect"]
        total = correct + incorrect
        return (correct / total * 100) if total > 0 else 0
    
    def get_weakest_numbers(self, count: int = 10) -> List[Tuple[str, float]]:
        """Get the numbers with lowest accuracy."""
        numbers_with_accuracy = []
        for number in self.stats:
            accuracy = self.get_accuracy(number)
            total_attempts = self.stats[number]["correct"] + self.stats[number]["incorrect"]
            # Prioritize numbers with low accuracy and some attempts
            priority_score = accuracy - (total_attempts * 0.1)  # Slight penalty for untested numbers
            numbers_with_accuracy.append((number, accuracy, priority_score))
        
        # Sort by priority score (lowest first)
        numbers_with_accuracy.sort(key=lambda x: x[2])
        return [(num, acc) for num, acc, _ in numbers_with_accuracy[:count]]
    
    def get_recent_numbers(self, hours: int = 24, count: int = 10) -> List[str]:
        """Get numbers tested within the last N hours."""
        if hours <= 0:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_numbers = []
        
        for number, stats in self.stats.items():
            if stats["last_tested"]:
                try:
                    last_tested = datetime.fromisoformat(stats["last_tested"])
                    if last_tested >= cutoff_time:
                        recent_numbers.append(number)
                except (ValueError, TypeError):
                    continue
        
        return recent_numbers[:count]
    
    def select_number_for_training(self) -> str:
        """Select a number for training using spaced repetition and weakness bias."""
        # Get recent numbers (last 2 hours for frequent review)
        very_recent = self.get_recent_numbers(hours=2, count=5)
        recent = self.get_recent_numbers(hours=8, count=10)
        
        # Get weakest numbers
        weak_numbers = [num for num, _ in self.get_weakest_numbers(15)]
        
        # Selection probabilities
        rand = random.random()
        
        if rand < 0.4 and very_recent:
            # 40% chance: Pick from very recent numbers (spaced repetition)
            return random.choice(very_recent)
        elif rand < 0.6 and recent:
            # 20% chance: Pick from recent numbers  
            return random.choice(recent)
        elif rand < 0.8 and weak_numbers:
            # 20% chance: Pick from weak numbers
            return random.choice(weak_numbers)
        else:
            # 20% chance: Completely random
            return f"{random.randint(0, 99):02d}"
    
    def display_header(self) -> None:
        """Display the application header."""
        print("\n" + "="*60)
        print("🧠 PAO MEMORY TRAINER 🧠")
        print("Person-Action-Object Association Training")
        print("="*60)
    
    def display_stats_summary(self) -> None:
        """Display overall statistics summary."""
        total_correct = sum(stat["correct"] for stat in self.stats.values())
        total_incorrect = sum(stat["incorrect"] for stat in self.stats.values())
        total_attempts = total_correct + total_incorrect
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total attempts: {total_attempts}")
        print(f"   Overall accuracy: {overall_accuracy:.1f}%")
        print(f"   Session: {self.session_stats['correct']}/{self.session_stats['total']} correct")
        
        # Show weakest numbers
        if total_attempts > 0:
            weak_numbers = self.get_weakest_numbers(5)
            print(f"\n🎯 WEAKEST ASSOCIATIONS:")
            for number, accuracy in weak_numbers:
                total = self.stats[number]["correct"] + self.stats[number]["incorrect"]
                if total > 0:
                    person = self.pao_data[number]['person']
                    print(f"   {number}: {person} ({accuracy:.0f}% - {total} attempts)")
    
    def test_number(self, number: str) -> bool:
        """Test user knowledge of a specific number."""
        pao = self.pao_data[number]
        
        # Check if this is the first time seeing this number
        total_attempts = self.stats[number]["correct"] + self.stats[number]["incorrect"]
        is_first_time = total_attempts == 0
        
        print(f"\n🔢 NUMBER: {number}")
        
        if is_first_time:
            print("📚 FIRST TIME SEEING THIS NUMBER - STUDY TIME!")
            print("="*50)
            print(f"Person: {pao['person']}")
            print(f"Action: {pao['action']}")
            print(f"Object: {pao['object']}")
            print("="*50)
            print("Take a moment to memorize this association...")
            
            # Give user time to study
            input("Press Enter when ready to be tested: ")
            
            # Clear the association from view
            print("\n" * 3)
            print("🧠 NOW TEST YOUR MEMORY!")
            print(f"🔢 NUMBER: {number}")
        
        print("What is the PAO association?")
        
        # Get user input for each component
        user_person = input("Person: ").strip()
        user_action = input("Action: ").strip()
        user_object = input("Object: ").strip()
        
        # Check answers (case-insensitive)
        correct_person = user_person.lower() == pao['person'].lower()
        correct_action = user_action.lower() == pao['action'].lower()
        correct_object = user_object.lower() == pao['object'].lower()
        
        all_correct = correct_person and correct_action and correct_object
        
        # Show results
        print(f"\n📝 RESULTS:")
        print(f"   Person: {'✓' if correct_person else '✗'} {pao['person']}")
        print(f"   Action: {'✓' if correct_action else '✗'} {pao['action']}")
        print(f"   Object: {'✓' if correct_object else '✗'} {pao['object']}")
        
        if all_correct:
            if is_first_time:
                print("🎉 EXCELLENT! You memorized it perfectly on first try!")
            else:
                print("🎉 PERFECT! All three components correct!")
        else:
            if is_first_time:
                print("📚 Good first attempt! Study this association and try again later.")
            else:
                print("📚 Study this association and try again later.")
        
        return all_correct
    
    def test_number_forward(self, number: str) -> bool:
        """Test user knowledge: given number, provide PAO."""
        pao = self.pao_data[number]
        
        print(f"\n🔢 NUMBER → PAO")
        print(f"Number: {number}")
        print("What is the PAO association?")
        
        # Get user input for each component
        user_person = input("Person: ").strip()
        user_action = input("Action: ").strip()
        user_object = input("Object: ").strip()
        
        # Check answers (case-insensitive)
        correct_person = user_person.lower() == pao['person'].lower()
        correct_action = user_action.lower() == pao['action'].lower()
        correct_object = user_object.lower() == pao['object'].lower()
        
        all_correct = correct_person and correct_action and correct_object
        
        # Show results
        print(f"\n📝 RESULTS:")
        print(f"   Person: {'✓' if correct_person else '✗'} {pao['person']}")
        print(f"   Action: {'✓' if correct_action else '✗'} {pao['action']}")
        print(f"   Object: {'✓' if correct_object else '✗'} {pao['object']}")
        
        return all_correct
    
    def test_number_reverse(self, number: str) -> bool:
        """Test user knowledge: given PAO, provide number."""
        pao = self.pao_data[number]
        
        print(f"\n🧠 PAO → NUMBER")
        print("Given this PAO association, what is the number?")
        print(f"Person: {pao['person']}")
        print(f"Action: {pao['action']}")
        print(f"Object: {pao['object']}")
        
        user_number = input("Number: ").strip()
        
        # Check answer (handle both with and without leading zero)
        correct = user_number == number or user_number == str(int(number))
        
        # Show results
        print(f"\n📝 RESULTS:")
        print(f"   Number: {'✓' if correct else '✗'} {number}")
        
        return correct
    
    def test_number_comprehensive(self, number: str) -> bool:
        """Test user knowledge with initial learning phase if needed."""
        pao = self.pao_data[number]
        
        # Check if this is the first time seeing this number
        total_attempts = self.stats[number]["correct"] + self.stats[number]["incorrect"]
        is_first_time = total_attempts == 0
        
        if is_first_time:
            print(f"\n🔢 NUMBER: {number}")
            print("📚 FIRST TIME SEEING THIS NUMBER - STUDY TIME!")
            print("="*50)
            print(f"Person: {pao['person']}")
            print(f"Action: {pao['action']}")
            print(f"Object: {pao['object']}")
            print("="*50)
            print("Take a moment to memorize this association...")
            
            # Give user time to study
            input("Press Enter when ready to be tested: ")
            
            # Clear the association from view
            print("\n" * 3)
            print("🧠 NOW TEST YOUR MEMORY!")
            
            # For first time, always test forward (number → PAO)
            correct = self.test_number_forward(number)
        else:
            # For repeat encounters, randomly choose test direction
            if random.random() < 0.5:
                correct = self.test_number_forward(number)
            else:
                correct = self.test_number_reverse(number)
        
        if correct:
            if is_first_time:
                print("🎉 EXCELLENT! You memorized it perfectly on first try!")
            else:
                print("🎉 PERFECT! Correct answer!")
        else:
            if is_first_time:
                print("📚 Good first attempt! Study this association and try again later.")
            else:
                print("📚 Study this association and try again later.")
                # Show the complete association for review
                print(f"\n📖 REVIEW:")
                print(f"   {number}: {pao['person']} → {pao['action']} → {pao['object']}")
        
        return correct
    
    def training_mode(self) -> None:
        """Main training loop."""
        print("\n🎯 TRAINING MODE")
        print("Commands: 'quit' to exit, 'stats' for detailed statistics")
        print("Using spaced repetition - recent questions will appear more frequently!")
        print("Press Enter to continue with smart number selection...")
        
        while True:
            try:
                # Use smart selection algorithm
                number = self.select_number_for_training()
                
                print("\n" + "-"*50)
                
                # Test the number
                correct = self.test_number_comprehensive(number)
                self.update_stats(number, correct)
                
                # Show current accuracy for this number
                accuracy = self.get_accuracy(number)
                total_attempts = self.stats[number]["correct"] + self.stats[number]["incorrect"]
                print(f"📈 Your accuracy for {number}: {accuracy:.0f}% ({total_attempts} attempts)")
                
                # Show selection reason for feedback
                very_recent = self.get_recent_numbers(hours=2, count=5)
                recent = self.get_recent_numbers(hours=8, count=10)
                weak_numbers = [num for num, _ in self.get_weakest_numbers(15)]
                
                if number in very_recent:
                    print("🔄 Selected for spaced repetition (very recent)")
                elif number in recent:
                    print("🔄 Selected for spaced repetition (recent)")
                elif number in weak_numbers:
                    print("💪 Selected for weakness improvement")
                else:
                    print("🎲 Selected randomly for variety")
                
                # Get user input for next action
                user_input = input("\nPress Enter for next number (or 'quit'/'stats'): ").strip().lower()
                
                if user_input == 'quit':
                    break
                elif user_input == 'stats':
                    self.show_detailed_stats()
                    input("\nPress Enter to continue training...")
                
            except KeyboardInterrupt:
                print("\n\nTraining interrupted. Saving progress...")
                break
            except EOFError:
                break
        
        self.save_stats()
        print("\n👋 Training session ended. Progress saved!")
    
    def show_detailed_stats(self) -> None:
        """Show detailed statistics for all numbers."""
        print("\n" + "="*80)
        print("📊 DETAILED STATISTICS")
        print("="*80)
        
        # Group by accuracy ranges
        ranges = {
            "🔥 Mastered (90-100%)": [],
            "✅ Good (70-89%)": [],
            "⚠️  Needs Work (50-69%)": [],
            "❌ Struggling (0-49%)": [],
            "❓ Untested": []
        }
        
        for number in sorted(self.stats.keys()):
            accuracy = self.get_accuracy(number)
            total = self.stats[number]["correct"] + self.stats[number]["incorrect"]
            person = self.pao_data[number]['person']
            
            if total == 0:
                ranges["❓ Untested"].append(f"{number}: {person}")
            elif accuracy >= 90:
                ranges["🔥 Mastered (90-100%)"].append(f"{number}: {person} ({accuracy:.0f}%)")
            elif accuracy >= 70:
                ranges["✅ Good (70-89%)"].append(f"{number}: {person} ({accuracy:.0f}%)")
            elif accuracy >= 50:
                ranges["⚠️  Needs Work (50-69%)"].append(f"{number}: {person} ({accuracy:.0f}%)")
            else:
                ranges["❌ Struggling (0-49%)"].append(f"{number}: {person} ({accuracy:.0f}%)")
        
        for category, numbers in ranges.items():
            if numbers:
                print(f"\n{category} ({len(numbers)}):")
                for entry in numbers[:10]:  # Show max 10 per category
                    print(f"   {entry}")
                if len(numbers) > 10:
                    print(f"   ... and {len(numbers) - 10} more")
    
    def browse_mode(self) -> None:
        """Browse all PAO associations."""
        print("\n📖 BROWSE MODE")
        print("Showing all PAO associations...")
        print("="*60)
        
        for number in sorted(self.pao_data.keys()):
            pao = self.pao_data[number]
            accuracy = self.get_accuracy(number)
            total = self.stats[number]["correct"] + self.stats[number]["incorrect"]
            
            status = ""
            if total > 0:
                status = f" [{accuracy:.0f}% - {total} attempts]"
            
            print(f"{number}: {pao['person']} → {pao['action']} → {pao['object']}{status}")
    
    def run(self, mode: str = "train") -> None:
        """Run the PAO trainer."""
        self.load_pao_data()
        self.display_header()
        self.display_stats_summary()
        
        if mode == "train":
            self.training_mode()
        elif mode == "browse":
            self.browse_mode()
        elif mode == "stats":
            self.show_detailed_stats()


def main():
    parser = argparse.ArgumentParser(description="PAO Memory Trainer")
    parser.add_argument("--mode", choices=["train", "browse", "stats"], default="train",
                       help="Training mode (default: train)")
    parser.add_argument("--csv", default="pao_00_99.csv",
                       help="PAO CSV file (default: pao_00_99.csv)")
    
    args = parser.parse_args()
    
    trainer = PAOTrainer(csv_file=args.csv)
    trainer.run(mode=args.mode)


if __name__ == "__main__":
    main() 