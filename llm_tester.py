import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import time
import requests
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from PIL import Image, ImageTk
import re
import sys
import io
import asyncio
import functools
import csv

class ModernUI:
    """Class for custom styling of the application"""
    THEME_LIGHT = {
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#3498db",
        "button": "#2980b9",
        "button_hover": "#3498db",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "error": "#e74c3c",
        "card_bg": "#ffffff",
        "border": "#e0e0e0",
        "font": ("Segoe UI", 10),
        "heading_font": ("Segoe UI", 12, "bold")
    }
    
    THEME_DARK = {
        "bg": "#2c3e50",
        "fg": "#ecf0f1",
        "accent": "#3498db",
        "button": "#2980b9",
        "button_hover": "#3498db",
        "success": "#2ecc71",
        "warning": "#f1c40f",
        "error": "#e74c3c",
        "card_bg": "#34495e",
        "border": "#7f8c8d",
        "font": ("Segoe UI", 10),
        "heading_font": ("Segoe UI", 12, "bold")
    }
    
    @staticmethod
    def setup_styles(theme="light"):
        """Setup ttk styles"""
        theme_values = ModernUI.THEME_LIGHT if theme == "light" else ModernUI.THEME_DARK
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure TButton
        style.configure(
            "TButton", 
            background=theme_values["button"],
            foreground=theme_values["fg"],
            font=theme_values["font"],
            padding=5,
            borderwidth=0
        )
        style.map(
            "TButton",
            background=[("active", theme_values["button_hover"])]
        )
        
        # Configure TLabel
        style.configure(
            "TLabel",
            background=theme_values["bg"],
            foreground=theme_values["fg"],
            font=theme_values["font"]
        )
        
        # Configure Heading
        style.configure(
            "Heading.TLabel",
            font=theme_values["heading_font"],
            background=theme_values["bg"],
            foreground=theme_values["fg"]
        )
        
        # Configure TFrame
        style.configure(
            "TFrame",
            background=theme_values["bg"]
        )
        
        # Configure Card.TFrame
        style.configure(
            "Card.TFrame",
            background=theme_values["card_bg"],
            borderwidth=1,
            relief="solid"
        )
        
        # Configure TNotebook
        style.configure(
            "TNotebook",
            background=theme_values["bg"],
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            "TNotebook.Tab",
            background=theme_values["button"],
            foreground=theme_values["fg"],
            padding=[10, 5],
            font=theme_values["font"]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", theme_values["accent"])],
            foreground=[("selected", "#ffffff")]
        )
        
        # Configure TCombobox
        style.configure(
            "TCombobox",
            background=theme_values["card_bg"],
            foreground=theme_values["fg"],
            fieldbackground=theme_values["card_bg"]
        )
        
        # Configure TEntry
        style.configure(
            "TEntry",
            background=theme_values["card_bg"],
            foreground=theme_values["fg"],
            fieldbackground=theme_values["card_bg"]
        )
        
        # Configure Success.TButton
        style.configure(
            "Success.TButton",
            background=theme_values["success"],
            foreground=theme_values["fg"]
        )
        style.map(
            "Success.TButton",
            background=[("active", theme_values["success"])]
        )
        
        # Configure Warning.TButton
        style.configure(
            "Warning.TButton",
            background=theme_values["warning"],
            foreground=theme_values["fg"]
        )
        style.map(
            "Warning.TButton",
            background=[("active", theme_values["warning"])]
        )
        
        # Configure Error.TButton
        style.configure(
            "Error.TButton",
            background=theme_values["error"],
            foreground=theme_values["fg"]
        )
        style.map(
            "Error.TButton",
            background=[("active", theme_values["error"])]
        )
        
        return theme_values


class LLMTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Performance Tester")
        self.root.geometry("1024x768")
        self.root.resizable(True, True)
        
        # Setup UI theme
        self.theme = "light"
        self.theme_values = ModernUI.setup_styles(self.theme)
        
        # Configure root background
        self.root.configure(bg=self.theme_values["bg"])
        
        # Variables
        self.current_profile = None
        self.profiles = self.load_profiles()
        self.test_results = self.load_test_results()
        self.available_models = {}
        
        # Create UI
        self.create_notebook()
        self.create_status_bar()
        
        # Center the window
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_status_bar(self):
        """Create a status bar at the bottom of the window."""
        self.status_bar = ttk.Frame(self.root, style="TFrame")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message
        self.status_message = ttk.Label(self.status_bar, text="Ready", style="TLabel")
        self.status_message.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Version info
        version_label = ttk.Label(self.status_bar, text="v1.0.0", style="TLabel")
        version_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def update_status(self, message, is_error=False):
        """Update the status bar message."""
        self.status_message.config(text=message)
        if is_error:
            self.status_message.config(foreground=self.theme_values["error"])
        else:
            self.status_message.config(foreground=self.theme_values["fg"])
        self.root.update_idletasks()
        
    def create_notebook(self):
        """Create the notebook with tabs."""
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_profiles_tab()
        self.create_test_tab()
        self.create_results_tab()
        self.create_settings_tab()
    
    def create_profiles_tab(self):
        """Create the profiles tab."""
        profiles_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(profiles_frame, text="Profiles")
        
        # Split into two frames
        left_frame = ttk.Frame(profiles_frame, style="Card.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=5, ipady=5)
        
        right_frame = ttk.Frame(profiles_frame, style="Card.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=5, ipady=5)
        
        # Left frame - Profile List
        ttk.Label(left_frame, text="Saved Profiles", style="Heading.TLabel").pack(pady=(10, 5))
        
        profile_frame = ttk.Frame(left_frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.profile_listbox = tk.Listbox(profile_frame, height=15, 
                                          bg=self.theme_values["card_bg"], 
                                          fg=self.theme_values["fg"],
                                          font=self.theme_values["font"],
                                          selectbackground=self.theme_values["accent"])
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(profile_frame, orient="vertical", command=self.profile_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_profile_listbox()
        
        # Add double-click binding to load profile
        self.profile_listbox.bind("<Double-1>", lambda e: self.load_profile())
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Button(btn_frame, text="Select for Testing", style="Success.TButton", command=self.load_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.load_profile_for_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", style="Error.TButton", command=self.delete_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="New", command=self.new_profile).pack(side=tk.RIGHT, padx=5)
        
        # Right frame - Profile Editor
        ttk.Label(right_frame, text="Profile Editor", style="Heading.TLabel").pack(pady=(10, 5))
        
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Profile name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Profile Name:").pack(side=tk.LEFT, padx=5)
        self.profile_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.profile_name_var, width=30).pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Provider type
        provider_frame = ttk.Frame(form_frame)
        provider_frame.pack(fill=tk.X, pady=5)
        ttk.Label(provider_frame, text="Provider:").pack(side=tk.LEFT, padx=5)
        self.provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var, width=30)
        provider_combo['values'] = ('OpenAI', 'Anthropic', 'OpenRouter', 'Custom')
        provider_combo.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        provider_combo.current(0)
        
        # API URL
        url_frame = ttk.Frame(form_frame)
        url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(url_frame, text="API URL:").pack(side=tk.LEFT, padx=5)
        self.api_url_var = tk.StringVar()
        self.api_url_var.set("https://api.openai.com/v1/chat/completions")
        ttk.Entry(url_frame, textvariable=self.api_url_var, width=30).pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # API Key
        key_frame = ttk.Frame(form_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API Key:").pack(side=tk.LEFT, padx=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.api_key_var, width=30, show="*").pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Model selection
        model_frame = ttk.Frame(form_frame)
        model_frame.pack(fill=tk.X, pady=5)
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        model_selection_frame = ttk.Frame(model_frame)
        model_selection_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        self.model_var = tk.StringVar()
        self.model_var.set("gpt-3.5-turbo")
        self.model_combo = ttk.Combobox(model_selection_frame, textvariable=self.model_var, width=25)
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Fetch models button
        fetch_models_btn = ttk.Button(model_selection_frame, text="Fetch Models", width=12, command=self.fetch_models)
        fetch_models_btn.pack(side=tk.RIGHT)
        
        # Content type
        content_frame = ttk.Frame(form_frame)
        content_frame.pack(fill=tk.X, pady=5)
        ttk.Label(content_frame, text="Content Type:").pack(side=tk.LEFT, padx=5)
        self.content_type_var = tk.StringVar(value="application/json")
        ttk.Entry(content_frame, textvariable=self.content_type_var, width=30).pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Button row
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Save Profile", style="Success.TButton", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_profile_form).pack(side=tk.RIGHT, padx=5)
        
        # Link provider selection to API URL update
        provider_combo.bind("<<ComboboxSelected>>", self.update_api_url)
    
    def new_profile(self):
        """Clear the form for a new profile."""
        self.clear_profile_form()
        self.update_status("Creating new profile")
    
    def clear_profile_form(self):
        """Clear the profile form."""
        self.profile_name_var.set("")
        self.provider_var.set("OpenAI")
        self.api_url_var.set("https://api.openai.com/v1/chat/completions")
        self.api_key_var.set("")
        self.model_var.set("gpt-3.5-turbo")
        self.content_type_var.set("application/json")
    
    def load_profile_for_edit(self):
        """Load the selected profile for editing."""
        self.load_profile(for_edit=True)
    
    def test_connection(self):
        """Test the connection to the API."""
        provider = self.provider_var.get()
        api_url = self.api_url_var.get()
        api_key = self.api_key_var.get()
        
        if not api_url or not api_key:
            messagebox.showerror("Error", "Please enter API URL and API Key")
            return
        
        self.update_status(f"Testing connection to {provider}...", False)
        
        # Create a simple test request
        headers = {
            "Content-Type": self.content_type_var.get(),
            "Authorization": f"Bearer {api_key}"
        }
        
        # Start a thread for the connection test
        thread = threading.Thread(target=self._test_connection, args=(api_url, headers))
        thread.daemon = True
        thread.start()
    
    def _test_connection(self, api_url, headers):
        """Perform the actual connection test."""
        try:
            # Just test the connection, don't make a full API call
            models_url = api_url
            
            # For OpenAI and similar APIs, use the models endpoint
            if "chat/completions" in api_url:
                models_url = api_url.replace("/chat/completions", "/models")
            
            response = requests.get(models_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.update_status("Connection successful", False)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Connection test successful!"))
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                self.update_status(f"Connection failed: {error_msg}", True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Connection test failed: {error_msg}"))
        
        except Exception as e:
            self.update_status(f"Connection error: {str(e)}", True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Connection test failed: {str(e)}"))
    
    def fetch_models(self):
        """Fetch available models from the API."""
        provider = self.provider_var.get()
        api_url = self.api_url_var.get()
        api_key = self.api_key_var.get()
        
        if not api_url or not api_key:
            messagebox.showerror("Error", "Please enter API URL and API Key")
            return
        
        self.update_status(f"Fetching models from {provider}...", False)
        
        # Determine models endpoint based on provider
        models_url = None
        
        if provider == "OpenAI":
            models_url = "https://api.openai.com/v1/models"
        elif provider == "OpenRouter":
            models_url = "https://openrouter.ai/api/v1/models"
        elif provider == "Anthropic":
            # Anthropic doesn't have a models endpoint, so we'll use a predefined list
            self.update_model_list([
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0",
                "claude-instant-1.2"
            ])
            return
        elif provider == "Custom" and "/chat/completions" in api_url:
            # Try to guess the models endpoint
            models_url = api_url.replace("/chat/completions", "/models")
        else:
            messagebox.showinfo("Info", "Model fetching not supported for this provider. Please enter the model name manually.")
            return
        
        # Create headers
        headers = {
            "Content-Type": self.content_type_var.get(),
            "Authorization": f"Bearer {api_key}"
        }
        
        # Start a thread for fetching models
        thread = threading.Thread(target=self._fetch_models, args=(models_url, headers, provider))
        thread.daemon = True
        thread.start()
    
    def _fetch_models(self, models_url, headers, provider):
        """Fetch models in a separate thread."""
        try:
            response = requests.get(models_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.update_status(f"Failed to fetch models: {response.status_code}", True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch models: {response.text}"))
                return
            
            data = response.json()
            models = []
            
            # Parse response based on provider
            if provider == "OpenAI":
                models = [model["id"] for model in data.get("data", [])]
            elif provider == "OpenRouter":
                models = [model["id"] for model in data.get("data", [])]
            else:
                # Generic attempt to extract model IDs
                if "data" in data and isinstance(data["data"], list):
                    models = [model.get("id") for model in data["data"] if "id" in model]
                elif "models" in data and isinstance(data["models"], list):
                    models = [model.get("id") for model in data["models"] if "id" in model]
                else:
                    # Try to find any list of models
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                            if "id" in value[0]:
                                models = [model.get("id") for model in value if "id" in model]
                                break
                            elif "name" in value[0]:
                                models = [model.get("name") for model in value if "name" in model]
                                break
            
            self.update_model_list(models)
            
        except Exception as e:
            self.update_status(f"Error fetching models: {str(e)}", True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch models: {str(e)}"))
    
    def update_model_list(self, models):
        """Update the model combobox with fetched models."""
        if not models:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No models found or unsupported response format."))
            return
            
        # Sort alphabetically
        models.sort()
        
        # Store models
        provider = self.provider_var.get()
        self.available_models[provider] = models
        
        # Update combobox
        self.model_combo['values'] = models
        
        # Set first model as current
        if models and self.model_var.get() not in models:
            self.model_var.set(models[0])
            
        self.update_status(f"Fetched {len(models)} models", False)
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully fetched {len(models)} models."))
        
    def create_test_tab(self):
        """Create the test tab."""
        test_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(test_frame, text="Run Test")
        
        # Top section - Profile selector
        profile_section = ttk.Frame(test_frame, style="Card.TFrame")
        profile_section.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(profile_section, text="Select Profile", style="Heading.TLabel").pack(pady=(10, 5))
        
        profiles_frame = ttk.Frame(profile_section)
        profiles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profile dropdown
        self.test_profile_var = tk.StringVar()
        self.profile_selector = ttk.Combobox(profiles_frame, textvariable=self.test_profile_var, width=40)
        self.profile_selector.pack(side=tk.LEFT, padx=5, pady=5)
        self.update_profile_selector()
        
        # Current profile info
        self.profile_info_label = ttk.Label(profile_section, text="No profile selected")
        self.profile_info_label.pack(pady=5, padx=10, anchor=tk.W)
        
        # Connect profile selector to update
        self.profile_selector.bind("<<ComboboxSelected>>", self.on_profile_selected)
        
        # Test configuration
        config_frame = ttk.LabelFrame(test_frame, text="Test Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Test parameters - Use a grid for better alignment
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Prompt
        ttk.Label(params_frame, text="Prompt:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.prompt_text = scrolledtext.ScrolledText(params_frame, height=5, width=60, font=self.theme_values["font"])
        self.prompt_text.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.prompt_text.insert(tk.END, "Write a creative story about a robot who wants to become human.")
        
        # Parameters row
        params_row = ttk.Frame(params_frame)
        params_row.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)
        
        # Max tokens
        ttk.Label(params_row, text="Max Tokens:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_tokens_var = tk.StringVar(value="1000")
        ttk.Entry(params_row, textvariable=self.max_tokens_var, width=8).pack(side=tk.LEFT, padx=(0, 15))
        
        # Temperature
        ttk.Label(params_row, text="Temperature:").pack(side=tk.LEFT, padx=(0, 5))
        self.temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(params_row, textvariable=self.temperature_var, width=5).pack(side=tk.LEFT, padx=(0, 15))
        
        # Number of runs
        ttk.Label(params_row, text="Number of Runs:").pack(side=tk.LEFT, padx=(0, 5))
        self.num_runs_var = tk.StringVar(value="3")
        ttk.Entry(params_row, textvariable=self.num_runs_var, width=5).pack(side=tk.LEFT)
        
        # Run button
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Run Test", style="Success.TButton", command=self.run_test).pack(pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(test_frame, text="Current Test Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                                    font=self.theme_values["font"],
                                                    bg=self.theme_values["card_bg"],
                                                    fg=self.theme_values["fg"])
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom button row
        bottom_button_frame = ttk.Frame(test_frame)
        bottom_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_button_frame, text="Save Results", command=self.save_test_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Copy to Clipboard", command=self.copy_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.RIGHT, padx=5)
    
    def update_profile_selector(self):
        """Update the profile selector dropdown."""
        profile_names = list(self.profiles.keys())
        profile_names.sort()
        self.profile_selector['values'] = profile_names
        
        if profile_names and self.test_profile_var.get() not in profile_names:
            if self.current_profile and self.current_profile in profile_names:
                self.test_profile_var.set(self.current_profile)
            elif profile_names:
                self.test_profile_var.set(profile_names[0])
    
    def on_profile_selected(self, event):
        """Handle profile selection from dropdown."""
        profile_name = self.test_profile_var.get()
        if profile_name in self.profiles:
            self.current_profile = profile_name
            profile = self.profiles[profile_name]
            
            # Update profile info display
            info_text = f"Provider: {profile.get('provider', 'Unknown')}\nModel: {profile.get('model', 'Unknown')}"
            self.profile_info_label.config(text=info_text)
            
            self.update_status(f"Selected profile: {profile_name}")
    
    def copy_results(self):
        """Copy results to clipboard."""
        if not hasattr(self, 'current_test_result') or not self.current_test_result:
            messagebox.showerror("Error", "No test results to copy")
            return
        
        try:
            result_text = self.results_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(result_text)
            self.update_status("Results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
    
    def clear_results(self):
        """Clear the results text."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)
        if hasattr(self, 'current_test_result'):
            delattr(self, 'current_test_result')
        self.update_status("Results cleared")
    
    def create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(settings_frame, text="Settings")
        
        # Create settings sections
        main_frame = ttk.Frame(settings_frame, style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App settings
        app_frame = ttk.LabelFrame(main_frame, text="Application Settings")
        app_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme selector
        theme_frame = ttk.Frame(app_frame)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="UI Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.theme_var = tk.StringVar(value=self.theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ('light', 'dark')
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        theme_combo.bind("<<ComboboxSelected>>", self.apply_theme)
        
        # Default parameters
        default_params_frame = ttk.LabelFrame(main_frame, text="Default Test Parameters")
        default_params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Max tokens
        ttk.Label(default_params_frame, text="Default Max Tokens:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.default_max_tokens_var = tk.StringVar(value="1000")
        ttk.Entry(default_params_frame, textvariable=self.default_max_tokens_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Temperature
        ttk.Label(default_params_frame, text="Default Temperature:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.default_temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(default_params_frame, textvariable=self.default_temperature_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Number of runs
        ttk.Label(default_params_frame, text="Default Number of Runs:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.default_num_runs_var = tk.StringVar(value="3")
        ttk.Entry(default_params_frame, textvariable=self.default_num_runs_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Data management
        data_frame = ttk.LabelFrame(main_frame, text="Data Management")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_frame = ttk.Frame(data_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Export All Results", command=self.export_results).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Import Results", command=self.import_results).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Clear All Results", style="Error.TButton", command=self.clear_all_results).pack(side=tk.LEFT, padx=5, pady=5)
        
        # About section
        about_frame = ttk.LabelFrame(main_frame, text="About")
        about_frame.pack(fill=tk.X, padx=10, pady=10)
        
        about_text = "LLM Performance Tester v1.0.0\n"
        about_text += "A tool for measuring and comparing LLM performance metrics.\n"
        about_text += "Created 2025"
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500)
        about_label.pack(padx=10, pady=10)
    
    def apply_theme(self, event):
        """Apply the selected theme."""
        self.theme = self.theme_var.get()
        self.theme_values = ModernUI.setup_styles(self.theme)
        
        # Update root background
        self.root.configure(bg=self.theme_values["bg"])
        
        # Update listbox colors
        listboxes = [self.profile_listbox, self.results_listbox]
        for listbox in listboxes:
            listbox.config(bg=self.theme_values["card_bg"], 
                         fg=self.theme_values["fg"],
                         selectbackground=self.theme_values["accent"])
        
        # Update text widgets
        text_widgets = [self.prompt_text, self.results_text]
        for widget in text_widgets:
            widget.config(bg=self.theme_values["card_bg"], fg=self.theme_values["fg"])
        
        self.update_status(f"Theme updated to {self.theme}")
    
    def export_results(self):
        """Export all test results to a file."""
        if not self.test_results:
            messagebox.showerror("Error", "No test results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Test Results"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as file:
                    json.dump(self.test_results, file, indent=4)
            elif file_path.endswith('.csv'):
                self.export_results_to_csv(file_path)
            else:
                with open(file_path, 'w') as file:
                    json.dump(self.test_results, file, indent=4)
            
            messagebox.showinfo("Success", f"Results exported to {file_path}")
            self.update_status(f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def export_results_to_csv(self, file_path):
        """Export results to CSV format."""
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['id', 'timestamp', 'profile', 'provider', 'model', 'avg_tps', 
                         'max_tokens', 'temperature', 'prompt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result_id, result in self.test_results.items():
                row = {
                    'id': result_id,
                    'timestamp': result.get('timestamp', ''),
                    'profile': result.get('profile', ''),
                    'provider': result.get('provider', ''),
                    'model': result.get('model', ''),
                    'avg_tps': result.get('avg_tps', 0),
                    'max_tokens': result.get('max_tokens', 0),
                    'temperature': result.get('temperature', 0),
                    'prompt': result.get('prompt', '')[:100]  # Truncate long prompts
                }
                writer.writerow(row)
    
    def export_selected_results(self):
        """Export only selected test results."""
        selected = self.results_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "No results selected for export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Selected Results"
        )
        
        if not file_path:
            return
        
        try:
            # Get the sorted results to match listbox order
            sorted_results = sorted(
                self.test_results.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )
            
            # Create a dict with only selected results
            selected_results = {}
            for index in selected:
                if index < len(sorted_results):
                    result_id = sorted_results[index][0]
                    if result_id in self.test_results:
                        selected_results[result_id] = self.test_results[result_id]
            
            if file_path.endswith('.json'):
                with open(file_path, 'w') as file:
                    json.dump(selected_results, file, indent=4)
            elif file_path.endswith('.csv'):
                # Reuse the CSV export function with selected results
                with open(file_path, 'w', newline='') as csvfile:
                    fieldnames = ['id', 'timestamp', 'profile', 'provider', 'model', 'avg_tps', 
                                'max_tokens', 'temperature', 'prompt']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for result_id, result in selected_results.items():
                        row = {
                            'id': result_id,
                            'timestamp': result.get('timestamp', ''),
                            'profile': result.get('profile', ''),
                            'provider': result.get('provider', ''),
                            'model': result.get('model', ''),
                            'avg_tps': result.get('avg_tps', 0),
                            'max_tokens': result.get('max_tokens', 0),
                            'temperature': result.get('temperature', 0),
                            'prompt': result.get('prompt', '')[:100]  # Truncate long prompts
                        }
                        writer.writerow(row)
            else:
                with open(file_path, 'w') as file:
                    json.dump(selected_results, file, indent=4)
            
            messagebox.showinfo("Success", f"Selected results exported to {file_path}")
            self.update_status(f"Selected results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export selected results: {str(e)}")
    
    def import_results(self):
        """Import test results from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Import Test Results"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as file:
                imported_results = json.load(file)
            
            # Validate the imported data
            if not isinstance(imported_results, dict):
                messagebox.showerror("Error", "Invalid results format: Expected a dictionary")
                return
            
            # Update or add the imported results
            for result_id, result in imported_results.items():
                self.test_results[result_id] = result
            
            # Save to file and update UI
            self.save_test_results_to_file()
            self.update_results_listbox()
            
            messagebox.showinfo("Success", f"Imported {len(imported_results)} test result(s)")
            self.update_status(f"Imported {len(imported_results)} test result(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import results: {str(e)}")
    
    def clear_all_results(self):
        """Clear all test results after confirmation."""
        if not self.test_results:
            messagebox.showinfo("Info", "No test results to clear")
            return
        
        confirmation = messagebox.askyesno(
            "Confirmation", 
            f"Are you sure you want to delete all {len(self.test_results)} test result(s)? This cannot be undone."
        )
        
        if confirmation:
            self.test_results = {}
            self.save_test_results_to_file()
            self.update_results_listbox()
            
            messagebox.showinfo("Success", "All test results cleared")
            self.update_status("All test results cleared")

    def create_results_tab(self):
        """Create the results comparison tab."""
        results_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(results_frame, text="Compare Results")
        
        # Split into two frames
        top_frame = ttk.Frame(results_frame, style="Card.TFrame")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        bottom_frame = ttk.Frame(results_frame, style="Card.TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - Results selection
        ttk.Label(top_frame, text="Saved Results:", style="Heading.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.results_listbox = tk.Listbox(top_frame, height=8, width=70, selectmode=tk.MULTIPLE, 
                                          bg=self.theme_values["card_bg"], fg=self.theme_values["fg"],
                                          font=self.theme_values["font"])
        self.results_listbox.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5, padx=5)
        
        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=self.results_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky=tk.NS, pady=5)
        self.results_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_results_listbox()
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Compare Selected", style="Success.TButton", command=self.compare_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", style="Error.TButton", command=self.delete_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Selected", command=self.export_selected_results).pack(side=tk.LEFT, padx=5)
        
        # Bottom frame - Comparison display
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, bottom_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def update_api_url(self, event):
        """Update the API URL based on the provider selection."""
        provider = self.provider_var.get()
        
        if provider == "OpenAI":
            self.api_url_var.set("https://api.openai.com/v1/chat/completions")
            self.model_var.set("gpt-3.5-turbo")
            self.content_type_var.set("application/json")
            # Update model combobox if we have OpenAI models cached
            if "OpenAI" in self.available_models:
                self.model_combo['values'] = self.available_models["OpenAI"]
                
        elif provider == "Anthropic":
            self.api_url_var.set("https://api.anthropic.com/v1/messages")
            self.model_var.set("claude-3-opus-20240229")
            self.content_type_var.set("application/json")
            # Update model combobox if we have Anthropic models cached
            if "Anthropic" in self.available_models:
                self.model_combo['values'] = self.available_models["Anthropic"]
                
        elif provider == "OpenRouter":
            self.api_url_var.set("https://openrouter.ai/api/v1/chat/completions")
            self.model_var.set("openai/gpt-3.5-turbo")
            self.content_type_var.set("application/json")
            # Update model combobox if we have OpenRouter models cached
            if "OpenRouter" in self.available_models:
                self.model_combo['values'] = self.available_models["OpenRouter"]
        
    def load_profiles(self):
        """Load profiles from file."""
        try:
            if os.path.exists('llm_profiles.json'):
                with open('llm_profiles.json', 'r') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
            return {}
    
    def save_profiles_to_file(self):
        """Save profiles to file."""
        try:
            with open('llm_profiles.json', 'w') as file:
                json.dump(self.profiles, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profiles: {str(e)}")
    
    def update_profile_listbox(self):
        """Update the profile listbox."""
        self.profile_listbox.delete(0, tk.END)
        profile_names = list(self.profiles.keys())
        profile_names.sort()
        
        for profile_name in profile_names:
            profile = self.profiles[profile_name]
            display_text = f"{profile_name} ({profile.get('provider', 'Unknown')} - {profile.get('model', 'Unknown')})"
            self.profile_listbox.insert(tk.END, display_text)
    
    def save_profile(self):
        """Save the current profile."""
        profile_name = self.profile_name_var.get().strip()
        
        if not profile_name:
            messagebox.showerror("Error", "Please enter a profile name")
            return
        
        if not self.api_key_var.get():
            messagebox.showwarning("Warning", "API Key is empty. Save anyway?")
        
        # Create profile
        profile = {
            "provider": self.provider_var.get(),
            "api_url": self.api_url_var.get(),
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "content_type": self.content_type_var.get(),
        }
        
        # Save profile
        self.profiles[profile_name] = profile
        self.save_profiles_to_file()
        self.update_profile_listbox()
        self.update_profile_selector()
        
        # Set as current profile
        self.current_profile = profile_name
        
        messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
        self.update_status(f"Profile '{profile_name}' saved successfully")
    
    def load_profile(self, for_edit=False):
        """Load the selected profile."""
        selected = self.profile_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a profile")
            return
        
        # Extract profile name from the display text (remove provider and model in parentheses)
        display_text = self.profile_listbox.get(selected[0])
        profile_name = display_text.split(" (")[0]
        
        profile = self.profiles.get(profile_name)
        
        if not profile:
            messagebox.showerror("Error", "Profile not found")
            return
        
        if for_edit:
            # Load profile data into form for editing
            self.profile_name_var.set(profile_name)
            self.provider_var.set(profile.get("provider", ""))
            self.api_url_var.set(profile.get("api_url", ""))
            self.api_key_var.set(profile.get("api_key", ""))
            self.model_var.set(profile.get("model", ""))
            self.content_type_var.set(profile.get("content_type", "application/json"))
            
            self.update_status(f"Loaded profile '{profile_name}' for editing")
        else:
            # Set as current profile for testing
            self.current_profile = profile_name
            
            # Update profile info in test tab
            self.test_profile_var.set(profile_name)
            info_text = f"Provider: {profile.get('provider', 'Unknown')}\nModel: {profile.get('model', 'Unknown')}"
            self.profile_info_label.config(text=info_text)
            
            # Switch to test tab
            self.notebook.select(1)  # Select the test tab (index 1)
            
            self.update_status(f"Profile '{profile_name}' selected for testing")
    
    def delete_profile(self):
        """Delete the selected profile."""
        selected = self.profile_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a profile")
            return
        
        # Extract profile name from the display text
        display_text = self.profile_listbox.get(selected[0])
        profile_name = display_text.split(" (")[0]
        
        if profile_name in self.profiles:
            confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete profile '{profile_name}'?")
            
            if confirmation:
                del self.profiles[profile_name]
                self.save_profiles_to_file()
                self.update_profile_listbox()
                self.update_profile_selector()
                
                if self.current_profile == profile_name:
                    self.current_profile = None
                
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully")
                self.update_status(f"Profile '{profile_name}' deleted successfully")
    
    def run_test(self):
        """Run the performance test."""
        profile_name = self.test_profile_var.get()
        
        if not profile_name or profile_name not in self.profiles:
            messagebox.showerror("Error", "Please select a valid profile first")
            return
        
        profile = self.profiles.get(profile_name)
        if not profile:
            messagebox.showerror("Error", "Profile not found")
            return
        
        # Get test parameters
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        try:
            max_tokens = int(self.max_tokens_var.get())
            temperature = float(self.temperature_var.get())
            num_runs = int(self.num_runs_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for max tokens, temperature, and number of runs")
            return
        
        # Clear results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Starting test with profile: {profile_name}\n")
        self.results_text.insert(tk.END, f"Model: {profile['model']}\n")
        self.results_text.insert(tk.END, f"Provider: {profile['provider']}\n")
        self.results_text.insert(tk.END, f"Running {num_runs} tests...\n\n")
        self.results_text.config(state=tk.DISABLED)
        self.root.update()
        
        # Update status
        self.update_status(f"Running test with {profile_name}...")
        
        # Run the test in a separate thread
        thread = threading.Thread(target=self.perform_test, args=(profile_name, profile, prompt, max_tokens, temperature, num_runs))
        thread.daemon = True
        thread.start()
    
    def perform_test(self, profile_name, profile, prompt, max_tokens, temperature, num_runs):
        """Perform the actual test."""
        api_url = profile["api_url"]
        api_key = profile["api_key"]
        model = profile["model"]
        provider = profile["provider"]
        content_type = profile.get("content_type", "application/json")
        
        # Prepare headers
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Bearer {api_key}"
        }
        
        # Add specific headers for certain providers
        if provider == "Anthropic":
            headers["anthropic-version"] = "2023-06-01"
        elif provider == "OpenRouter":
            headers["HTTP-Referer"] = "localhost"  # OpenRouter requires HTTP-Referer
        
        results = []
        
        for i in range(num_runs):
            self.update_results_text(f"Run {i+1}/{num_runs}...\n")
            
            # Prepare request based on provider
            if provider == "OpenAI" or provider == "OpenRouter":
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            elif provider == "Anthropic":
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            else:  # Custom
                # Try to guess the format based on the API URL
                if "chat/completions" in api_url:
                    # OpenAI-like format
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                else:
                    # Generic format with model as parameter
                    data = {
                        "model": model,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
            
            try:
                # Make the request
                start_time = time.time()
                response = requests.post(api_url, headers=headers, json=data, timeout=120)
                end_time = time.time()
                
                if response.status_code != 200:
                    error_msg = f"Error: {response.status_code} - {response.text}\n"
                    self.update_results_text(error_msg)
                    self.update_status(f"Error in run {i+1}", True)
                    continue
                
                # Parse response based on provider
                response_data = response.json()
                tokens_generated = 0
                generated_text = ""
                
                if provider == "OpenAI" or provider == "OpenRouter":
                    tokens_generated = response_data.get("usage", {}).get("completion_tokens", 0)
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        message = response_data["choices"][0].get("message", {})
                        generated_text = message.get("content", "")
                        
                    if tokens_generated == 0 and generated_text:
                        # Estimate tokens from content length
                        tokens_generated = len(generated_text.split()) * 1.3  # Rough estimate
                        
                elif provider == "Anthropic":
                    if "content" in response_data and len(response_data["content"]) > 0:
                        content_item = response_data["content"][0]
                        if "text" in content_item:
                            generated_text = content_item["text"]
                    
                    # Anthropic may provide usage info
                    if "usage" in response_data:
                        tokens_generated = response_data["usage"].get("output_tokens", 0)
                    else:
                        # Estimate tokens from generated text
                        tokens_generated = len(generated_text.split()) * 1.3  # Rough estimate
                
                else:
                    # Try to extract token count or estimate from various response formats
                    if "usage" in response_data and "completion_tokens" in response_data["usage"]:
                        tokens_generated = response_data["usage"]["completion_tokens"]
                    elif "choices" in response_data and len(response_data["choices"]) > 0:
                        if "text" in response_data["choices"][0]:
                            generated_text = response_data["choices"][0]["text"]
                        elif "message" in response_data["choices"][0]:
                            generated_text = response_data["choices"][0]["message"].get("content", "")
                            
                        tokens_generated = len(generated_text.split()) * 1.3  # Rough estimate
                    elif "output" in response_data:
                        generated_text = response_data["output"]
                        tokens_generated = len(generated_text.split()) * 1.3  # Rough estimate
                
                # Calculate TPS
                duration = end_time - start_time
                tps = tokens_generated / duration if duration > 0 else 0
                
                results.append({
                    "run": i + 1,
                    "tokens_generated": tokens_generated,
                    "duration": duration,
                    "tps": tps,
                    "first_50_chars": generated_text[:50] + "..." if generated_text else ""
                })
                
                result_text = f"Run {i+1} completed: {tokens_generated:.0f} tokens in {duration:.2f}s = {tps:.2f} TPS\n"
                self.update_results_text(result_text)
                self.update_status(f"Completed run {i+1}/{num_runs}")
                
            except Exception as e:
                error_text = f"Error in run {i+1}: {str(e)}\n"
                self.update_results_text(error_text)
                self.update_status(f"Error in run {i+1}: {str(e)}", True)
        
        # Calculate average TPS
        if results:
            avg_tps = sum(result["tps"] for result in results) / len(results)
            self.update_results_text(f"\nAverage TPS: {avg_tps:.2f}\n")
            
            # Show sample of generated text
            if results[0].get("first_50_chars"):
                self.update_results_text(f"\nSample output: {results[0]['first_50_chars']}\n")
            
            # Store the test result
            test_result = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile": profile_name,
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "runs": results,
                "avg_tps": avg_tps
            }
            
            self.current_test_result = test_result
            self.update_status(f"Test completed - Avg TPS: {avg_tps:.2f}")
        else:
            self.update_status("Test failed - no valid results", True)
    
    def update_results_text(self, text):
        """Update the results text widget from any thread."""
        self.root.after(0, self._update_results_text, text)
    
    def _update_results_text(self, text):
        """Update the results text widget (must be called from main thread)."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def save_test_results(self):
        """Save the current test results."""
        if not hasattr(self, 'current_test_result') or not self.current_test_result:
            messagebox.showerror("Error", "No test results to save")
            return
        
        # Generate a unique ID for the test
        result_id = f"{self.current_test_result['provider']}_{self.current_test_result['model']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save the result
        self.test_results[result_id] = self.current_test_result
        self.save_test_results_to_file()
        
        # Update the results listbox
        self.update_results_listbox()
        
        messagebox.showinfo("Success", "Test results saved successfully")
        self.update_status("Test results saved successfully")
    
    def load_test_results(self):
        """Load test results from file."""
        try:
            if os.path.exists('llm_test_results.json'):
                with open('llm_test_results.json', 'r') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load test results: {str(e)}")
            return {}
    
    def save_test_results_to_file(self):
        """Save test results to file."""
        try:
            with open('llm_test_results.json', 'w') as file:
                json.dump(self.test_results, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save test results: {str(e)}")
    
    def update_results_listbox(self):
        """Update the results listbox."""
        self.results_listbox.delete(0, tk.END)
        
        # Sort results by timestamp (newest first)
        sorted_results = sorted(
            self.test_results.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        for result_id, result in sorted_results:
            display_text = (
                f"{result.get('timestamp', 'Unknown')} - "
                f"{result.get('provider', 'Unknown')} - "
                f"{result.get('model', 'Unknown')} - "
                f"Avg TPS: {result.get('avg_tps', 0):.2f}"
            )
            self.results_listbox.insert(tk.END, display_text)
            # Store the result_id as an item attribute
            self.results_listbox.itemconfig(tk.END, {"result_id": result_id})
    
    def delete_results(self):
        """Delete the selected test results."""
        selected = self.results_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "Please select at least one result to delete")
            return
        
        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {len(selected)} test result(s)?")
        
        if confirmation:
            # Get the sorted results to match listbox order
            sorted_results = sorted(
                self.test_results.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )
            
            # Delete selected results
            for index in sorted(selected, reverse=True):
                if index < len(sorted_results):
                    result_id = sorted_results[index][0]
                    if result_id in self.test_results:
                        del self.test_results[result_id]
            
            # Save and update
            self.save_test_results_to_file()
            self.update_results_listbox()
            
            messagebox.showinfo("Success", "Test result(s) deleted successfully")
            self.update_status("Test result(s) deleted successfully")
    
    def compare_results(self):
        """Compare the selected test results."""
        selected = self.results_listbox.curselection()
        
        if not selected or len(selected) < 1:
            messagebox.showerror("Error", "Please select at least one result to compare")
            return
        
        # Get the sorted results to match listbox order
        sorted_results = sorted(
            self.test_results.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        # Get the selected results
        results_to_compare = []
        for index in selected:
            if index < len(sorted_results):
                result_id = sorted_results[index][0]
                if result_id in self.test_results:
                    results_to_compare.append((result_id, self.test_results[result_id]))
        
        if not results_to_compare:
            messagebox.showerror("Error", "No valid results to compare")
            return
        
        # Clear the chart
        self.ax.clear()
        
        # Plot the results
        labels = []
        tps_values = []
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', 
                 '#1abc9c', '#d35400', '#34495e', '#7f8c8d', '#2c3e50']
        
        for i, (result_id, result) in enumerate(results_to_compare):
            label = f"{result.get('provider', 'Unknown')}-{result.get('model', 'Unknown')}"
            tps = result.get('avg_tps', 0)
            
            labels.append(label)
            tps_values.append(tps)
        
        # Create the bar chart with custom colors
        bars = self.ax.bar(labels, tps_values, color=[colors[i % len(colors)] for i in range(len(labels))])
        
        # Add labels
        self.ax.set_xlabel('Model')
        self.ax.set_ylabel('Tokens Per Second (TPS)')
        self.ax.set_title('LLM Performance Comparison')
        
        # Rotate x-axis labels if we have many models
        if len(labels) > 3:
            self.ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                         f'{height:.2f}', ha='center', va='bottom')
        
        # Add grid lines for better readability
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Redraw the canvas
        self.chart_canvas.draw()
        
        self.update_status(f"Comparing {len(results_to_compare)} result(s)")

def main():
    root = tk.Tk()
    app = LLMTesterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()