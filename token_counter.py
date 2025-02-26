#!/usr/bin/env python3
"""
Token Counter Utility for LLM Performance Tester

This script provides a simple way to estimate the number of tokens in text.
It can be used to better understand token usage when designing prompts for LLM testing.

Note: This is an approximation. Different tokenizers will produce slightly different results.
"""

import re
import argparse
import tkinter as tk
from tkinter import ttk, scrolledtext

class TokenCounter:
    def __init__(self):
        """Initialize the token counter with regex patterns."""
        # Simple regex-based tokenization (approximation)
        self.pattern = re.compile(r'\w+|[^\w\s]')
        
        # More complex pattern that better approximates GPT tokenization (still an estimate)
        self.gpt_pattern = re.compile(r'''(?x)
            (?:[A-Z]\.)+|[A-Z][a-z]+(?=[A-Z])|[\w]+|
            [.,!?;:@#$%^&*()[\]{}|/<>~`'\"\-=_+]|
            \s+
        ''')
    
    def count_tokens_simple(self, text):
        """
        Count tokens using a simple word/punctuation split.
        This is a baseline approximation.
        """
        if not text:
            return 0
        tokens = self.pattern.findall(text)
        return len(tokens)
    
    def count_tokens_gpt_estimate(self, text):
        """
        Count tokens using a more sophisticated regex that better
        approximates GPT-style tokenization. Still an approximation.
        """
        if not text:
            return 0
        tokens = self.gpt_pattern.findall(text)
        
        # Adjust for common subword token patterns
        token_count = len(tokens)
        
        # Correction factor for subword tokenization
        # Empirically, GPT tends to use ~1.3x more tokens than word count for English
        correction = 1.3
        
        return int(token_count * correction)
    
    def count_tokens_by_chars(self, text):
        """
        Estimate tokens based on character count.
        Roughly 4 characters per token for English text.
        """
        if not text:
            return 0
        char_count = len(text)
        return char_count // 4

class TokenCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Token Counter Utility")
        self.root.geometry("600x500")
        
        self.counter = TokenCounter()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for input
        input_frame = ttk.LabelFrame(self.root, text="Input Text")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_input = scrolledtext.ScrolledText(input_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button to count tokens
        count_button = ttk.Button(self.root, text="Count Tokens", command=self.count_tokens)
        count_button.pack(pady=10)
        
        # Frame for displaying results
        results_frame = ttk.LabelFrame(self.root, text="Token Counts")
        results_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Results display
        self.results_var = {
            "simple": tk.StringVar(value="0 tokens"),
            "gpt": tk.StringVar(value="0 tokens"),
            "char": tk.StringVar(value="0 tokens")
        }
        
        # Simple count
        simple_frame = ttk.Frame(results_frame)
        simple_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(simple_frame, text="Simple Word Count:").pack(side=tk.LEFT)
        ttk.Label(simple_frame, textvariable=self.results_var["simple"]).pack(side=tk.RIGHT)
        
        # GPT estimate
        gpt_frame = ttk.Frame(results_frame)
        gpt_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(gpt_frame, text="GPT-style Estimate (recommended):").pack(side=tk.LEFT)
        ttk.Label(gpt_frame, textvariable=self.results_var["gpt"]).pack(side=tk.RIGHT)
        
        # Character-based estimate
        char_frame = ttk.Frame(results_frame)
        char_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(char_frame, text="Character-based Estimate:").pack(side=tk.LEFT)
        ttk.Label(char_frame, textvariable=self.results_var["char"]).pack(side=tk.RIGHT)
        
        # Info text
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = """Note: These are approximations. Actual token counts may vary by model.
The GPT-style estimate is generally closest to OpenAI's tokenization."""
        
        ttk.Label(info_frame, text=info_text, wraplength=580, justify=tk.LEFT).pack()
        
        # Add sample prompts dropdown
        sample_frame = ttk.Frame(self.root)
        sample_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(sample_frame, text="Sample Prompts:").pack(side=tk.LEFT, padx=(0, 5))
        
        samples = [
            "Select a sample...",
            "Write a short poem about artificial intelligence.",
            "Explain the difference between supervised and unsupervised learning in machine learning.",
            "Write a creative story about a robot who wants to become human."
        ]
        
        self.sample_var = tk.StringVar()
        self.sample_var.set(samples[0])
        
        sample_combo = ttk.Combobox(sample_frame, textvariable=self.sample_var, values=samples, width=50)
        sample_combo.pack(side=tk.LEFT, padx=5)
        sample_combo.bind("<<ComboboxSelected>>", self.load_sample)
        
    def count_tokens(self):
        """Count tokens using various methods and update the display."""
        text = self.text_input.get("1.0", tk.END).strip()
        
        # Get counts
        simple_count = self.counter.count_tokens_simple(text)
        gpt_count = self.counter.count_tokens_gpt_estimate(text)
        char_count = self.counter.count_tokens_by_chars(text)
        
        # Update display
        self.results_var["simple"].set(f"{simple_count} tokens")
        self.results_var["gpt"].set(f"{gpt_count} tokens")
        self.results_var["char"].set(f"{char_count} tokens")
    
    def load_sample(self, event):
        """Load a sample prompt into the text input."""
        sample = self.sample_var.get()
        
        if sample != "Select a sample...":
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", sample)
            self.count_tokens()

def main_gui():
    """Run the GUI application."""
    root = tk.Tk()
    app = TokenCounterApp(root)
    root.mainloop()

def main_cli():
    """Run the CLI application."""
    parser = argparse.ArgumentParser(description="Estimate token counts for text.")
    parser.add_argument("--text", type=str, help="Text to count tokens for")
    parser.add_argument("--file", type=str, help="File containing text to count tokens for")
    args = parser.parse_args()
    
    counter = TokenCounter()
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("Please provide text using --text or --file")
        return
    
    simple_count = counter.count_tokens_simple(text)
    gpt_count = counter.count_tokens_gpt_estimate(text)
    char_count = counter.count_tokens_by_chars(text)
    
    print(f"Simple word count: {simple_count} tokens")
    print(f"GPT-style estimate: {gpt_count} tokens")
    print(f"Character-based estimate: {char_count} tokens")

if __name__ == "__main__":
    # Check if any CLI arguments were provided
    import sys
    if len(sys.argv) > 1:
        main_cli()
    else:
        main_gui()