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
import csv
import sv_ttk  # Sun Valley theme

class LLMTesterApp:
    # Standardized prompt templates for benchmarking
    BENCHMARK_PROMPTS = {
        # COMPLETION PROMPTS
        "Completion (Short)": "Generate a list of 5 ideas for improving user engagement in a mobile application.",
        
        "Completion (Medium)": "Provide a comprehensive overview of machine learning algorithms, their applications, and limitations. Include examples of when each type would be most appropriate.",
        
        "Completion (Long)": "Write a detailed technical report on renewable energy technologies, comparing solar, wind, hydroelectric, and geothermal power. Include analysis of efficiency, cost, environmental impact, and future potential.",
        
        # CREATIVE PROMPTS
        "Creative (Short)": "Write a short poem about artificial intelligence that rhymes.",
        
        "Creative (Medium)": "Write a short story about a character who discovers an unusual ability. Include dialogue and sensory details.",
        
        "Creative (Long)": "Write a detailed short story about a world where time moves backwards. Include character development, dialogue, and a satisfying conclusion.",
        
        # REASONING PROMPTS
        "Reasoning (Simple)": "A student scored 80% on a test with 25 questions. How many questions did they answer correctly? Explain your reasoning step by step.",
        
        "Reasoning (Medium)": "Explain the trolley problem and analyze the ethical implications from utilitarian and deontological perspectives. Present arguments for both viewpoints.",
        
        "Reasoning (Complex)": "Design a system to optimize traffic flow in a major city. Consider infrastructure, technology, public transportation, and incentive structures. Address potential challenges and propose solutions.",
        
        # TECHNICAL PROMPTS
        "Technical (Simple)": "Explain the concept of cloud computing to a non-technical person. Include its benefits and common applications.",
        
        "Technical (Medium)": "Compare and contrast SQL and NoSQL databases. Explain when to use each type and provide specific examples of database systems.",
        
        "Technical (Complex)": "Explain how transformer neural networks work in natural language processing, including attention mechanisms and how they differ from recurrent neural networks.",
        
        # DOMAIN-SPECIFIC PROMPTS
        "Domain - Medical": "Explain the relationship between inflammation, autoimmune disorders, and the microbiome. Include recent research findings and potential therapeutic approaches.",
        
        "Domain - Legal": "Analyze the legal implications of artificial intelligence regarding intellectual property, liability, and privacy. Reference relevant laws and precedents.",
        
        "Domain - Financial": "Explain modern portfolio theory, diversification strategies, and approaches to risk management in investment. Include practical applications for individual investors."
    }

    def __init__(self, root):
        self.root = root
        self.root.title("LLM Performance Tester")
        self.root.geometry("1024x768")
        self.root.resizable(True, True)
        
        # Apply Sun Valley theme
        sv_ttk.set_theme("light")
        
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
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message
        self.status_message = ttk.Label(self.status_bar, text="Ready")
        self.status_message.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Version info
        version_label = ttk.Label(self.status_bar, text="v1.0.0")
        version_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def update_status(self, message, is_error=False):
        """Update the status bar message."""
        self.status_message.config(text=message)
        if is_error:
            self.status_message.config(foreground="red")
        else:
            self.status_message.config(foreground="black")
        self.root.update_idletasks()
        
    def create_notebook(self):
        """Create the notebook with tabs."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_profiles_tab()
        self.create_test_tab()
        self.create_compare_tab()  # New comparison tab
        self.create_results_tab()
        self.create_settings_tab()
    
    def create_profiles_tab(self):
        """Create the profiles tab."""
        profiles_frame = ttk.Frame(self.notebook)
        self.notebook.add(profiles_frame, text="Profiles")
        
        # Split into two frames
        left_frame = ttk.LabelFrame(profiles_frame, text="Saved Profiles")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ttk.LabelFrame(profiles_frame, text="Profile Editor")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Profile List with profile filtering
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_var.trace("w", lambda name, index, mode: self.update_profile_listbox())
        
        # Profile list with scrollbar
        profile_frame = ttk.Frame(left_frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.profile_listbox = tk.Listbox(profile_frame, height=15)
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(profile_frame, orient="vertical", command=self.profile_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_profile_listbox()
        
        # Add double-click binding to load profile
        self.profile_listbox.bind("<Double-1>", lambda e: self.load_profile())
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Button(btn_frame, text="Select for Testing", command=self.load_profile, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.load_profile_for_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="New", command=self.new_profile).pack(side=tk.RIGHT, padx=5)
        
        # Right frame - Profile Editor
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
        
        # Endpoint Configuration
        endpoint_frame = ttk.LabelFrame(form_frame, text="API Endpoint")
        endpoint_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Base URL
        base_url_frame = ttk.Frame(endpoint_frame)
        base_url_frame.pack(fill=tk.X, pady=10)
        ttk.Label(base_url_frame, text="Base API URL:").pack(side=tk.LEFT, padx=5)
        self.base_url_var = tk.StringVar()
        self.base_url_var.set("https://api.openai.com/v1")
        ttk.Entry(base_url_frame, textvariable=self.base_url_var, width=30).pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Help text
        ttk.Label(endpoint_frame, text="Standard formats: https://api.openai.com/v1, https://api.anthropic.com/v1, https://router.requesty.ai/v1",
                 font=("TkDefaultFont", 8), foreground="gray").pack(anchor=tk.W, padx=10, pady=(0,5))
        
        # API Key 
        key_frame = ttk.Frame(form_frame)
        key_frame.pack(fill=tk.X, pady=10)
        ttk.Label(key_frame, text="API Key:").pack(side=tk.LEFT, padx=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.api_key_var, width=30, show="*").pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Show/Hide API Key button
        show_key_btn = ttk.Button(key_frame, text="👁", width=3, command=self.toggle_api_key_visibility)
        show_key_btn.pack(side=tk.RIGHT, padx=0)
        # Model selection
        model_frame = ttk.Frame(form_frame)
        model_frame.pack(fill=tk.X, pady=5)
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        model_selection_frame = ttk.Frame(model_frame)
        model_selection_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Model entry mode
        self.model_entry_mode = tk.StringVar(value="dropdown")
        
        # Create container for both input methods
        model_input_container = ttk.Frame(model_selection_frame)
        model_input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.model_var = tk.StringVar()
        self.model_var.set("gpt-3.5-turbo")
        
        # Dropdown mode
        self.model_combo = ttk.Combobox(model_input_container, textvariable=self.model_var, width=25)
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Manual entry mode
        self.model_entry = ttk.Entry(model_input_container, textvariable=self.model_var, width=25)
        
        # Status label for model fetching
        self.model_status_label = ttk.Label(model_selection_frame, text="", font=("TkDefaultFont", 8))
        self.model_status_label.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
        
        # Buttons frame
        model_buttons_frame = ttk.Frame(model_selection_frame)
        model_buttons_frame.pack(side=tk.RIGHT)
        
        # Toggle switch between dropdown and manual entry
        self.toggle_model_entry_btn = ttk.Button(
            model_buttons_frame,
            text="📝",
            width=3,
            command=self.toggle_model_entry_mode
        )
        self.toggle_model_entry_btn.pack(side=tk.LEFT)
        
        # Create tooltip for the toggle button
        self.create_tooltip(self.toggle_model_entry_btn, "Switch between dropdown and manual entry")
        
        # Fetch models button
        self.fetch_models_btn = ttk.Button(model_buttons_frame, text="Fetch Models", width=12, command=self.fetch_models)
        self.fetch_models_btn.pack(side=tk.LEFT, padx=(3, 0))
        
        # Content type
        content_frame = ttk.Frame(form_frame)
        content_frame.pack(fill=tk.X, pady=5)
        ttk.Label(content_frame, text="Content Type:").pack(side=tk.LEFT, padx=5)
        self.content_type_var = tk.StringVar(value="application/json")
        ttk.Entry(content_frame, textvariable=self.content_type_var, width=30).pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Additional headers
        headers_frame = ttk.Frame(form_frame)
        headers_frame.pack(fill=tk.X, pady=5)
        ttk.Label(headers_frame, text="Additional Headers:").pack(side=tk.LEFT, padx=5, anchor=tk.N)
        
        headers_scroll_frame = ttk.Frame(headers_frame)
        headers_scroll_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.headers_text = scrolledtext.ScrolledText(headers_scroll_frame, height=5, width=30, wrap=tk.WORD)
        self.headers_text.pack(fill=tk.X, expand=True)
        self.headers_text.insert(tk.END, '{}')
        
        # Button row
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Save Profile", command=self.save_profile, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_profile_form).pack(side=tk.RIGHT, padx=5)
        
        # Link provider selection to API URL update
        provider_combo.bind("<<ComboboxSelected>>", self.update_api_url)
    
    def toggle_api_key_visibility(self):
        """Toggle the visibility of the API key."""
        key_entry = self.api_key_var.get()
        if key_entry:
            current_show = self.root.nametowidget(self.root.focus_get()).cget("show")
            if current_show == "*":
                self.root.nametowidget(self.root.focus_get()).config(show="")
            else:
                self.root.nametowidget(self.root.focus_get()).config(show="*")
    
    def new_profile(self):
        """Clear the form for a new profile."""
        self.clear_profile_form()
        self.update_status("Creating new profile")
    
    def clear_profile_form(self):
        """Clear the profile form."""
        self.profile_name_var.set("")
        self.provider_var.set("OpenAI")
        self.base_url_var.set("https://api.openai.com/v1")
        self.api_key_var.set("")
        self.model_var.set("gpt-3.5-turbo")
        self.content_type_var.set("application/json")
        self.headers_text.delete("1.0", tk.END)
        self.headers_text.insert(tk.END, '{}')
    
    def load_profile_for_edit(self):
        """Load the selected profile for editing."""
        self.load_profile(for_edit=True)
    
    def test_connection(self):
        """Test the connection to the API."""
        provider = self.provider_var.get()
        base_url = self.base_url_var.get()
        api_key = self.api_key_var.get()
        
        if not base_url or not api_key:
            messagebox.showerror("Error", "Please enter Base API URL and API Key")
            return
        
        self.update_status(f"Testing connection to {provider}...", False)
        
        # Construct the models URL from the base URL
        models_url = f"{base_url.rstrip('/')}/models"
        
        # Create headers
        try:
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            additional_headers = json.loads(headers_text) if headers_text else {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in additional headers")
            return
        
        headers = {
            "Content-Type": self.content_type_var.get(),
            "Authorization": f"Bearer {api_key}"
        }
        headers.update(additional_headers)
        
        # Start a thread for the connection test
        thread = threading.Thread(target=self._test_connection, args=(models_url, headers))
        thread.daemon = True
        thread.start()
    
    def _test_connection(self, models_url, headers):
        """Perform the actual connection test."""
        try:
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
        base_url = self.base_url_var.get()
        api_key = self.api_key_var.get()
        
        if not base_url or not api_key:
            messagebox.showerror("Error", "Please enter Base API URL and API Key")
            return
        
        self.update_status(f"Fetching models from {provider}...", False)
        
        # Create headers
        try:
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            additional_headers = json.loads(headers_text) if headers_text else {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in additional headers")
            return
            
        headers = {
            "Content-Type": self.content_type_var.get(),
            "Authorization": f"Bearer {api_key}"
        }
        headers.update(additional_headers)
        
        # Handle Anthropic special case
        if provider == "Anthropic":
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
        
        # Construct the models URL from the base URL
        models_url = f"{base_url.rstrip('/')}/models"
            
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
            self.model_status_label.config(text="No models found")
            self.root.after(0, lambda: messagebox.showinfo("Info", "No models found or unsupported response format."))
            return
            
        # Sort alphabetically
        models.sort()
        
        # Store models
        provider = self.provider_var.get()
        self.available_models[provider] = models
        
        # Update combobox
        self.model_combo['values'] = models
        
        # Set first model as current if current value not in list
        if models and self.model_var.get() not in models:
            self.model_var.set(models[0])
            
        # Switch to dropdown mode if we're in manual mode
        if self.model_entry_mode.get() == "manual" and models:
            self.toggle_model_entry_mode()
            
        # Update status
        self.model_status_label.config(text=f"Loaded {len(models)} models")
        self.update_status(f"Fetched {len(models)} models", False)
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully fetched {len(models)} models."))
        
        # Update the comparison tab selectors
        if hasattr(self, 'profile1_selector') and hasattr(self, 'profile2_selector'):
            self.update_compare_profile_selectors()
        
    def create_test_tab(self):
        """Create the test tab."""
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="Run Test")
        
        # Top section - Profile selector
        profile_section = ttk.LabelFrame(test_frame, text="Select Profile")
        profile_section.pack(fill=tk.X, padx=10, pady=10)
        
        profiles_frame = ttk.Frame(profile_section)
        profiles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profile dropdown
        ttk.Label(profiles_frame, text="Profile:").pack(side=tk.LEFT, padx=5, pady=5)
        self.test_profile_var = tk.StringVar()
        self.profile_selector = ttk.Combobox(profiles_frame, textvariable=self.test_profile_var, width=40)
        self.profile_selector.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.update_profile_selector()
        
        # Manage Profiles button
        ttk.Button(profiles_frame, text="Manage Profiles", command=self.go_to_profiles_tab).pack(side=tk.LEFT, padx=5)
        
        # Current profile info
        self.profile_info_frame = ttk.Frame(profile_section)
        self.profile_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.provider_label = ttk.Label(self.profile_info_frame, text="Provider: None")
        self.provider_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.model_label = ttk.Label(self.profile_info_frame, text="Model: None")
        self.model_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.url_label = ttk.Label(self.profile_info_frame, text="API URL: None")
        self.url_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        # Connect profile selector to update
        self.profile_selector.bind("<<ComboboxSelected>>", self.on_profile_selected)
        
        # Test configuration
        config_frame = ttk.LabelFrame(test_frame, text="Test Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Prompt Selection
        prompt_selection_frame = ttk.Frame(config_frame)
        prompt_selection_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        ttk.Label(prompt_selection_frame, text="Benchmark Prompt:").pack(side=tk.LEFT, padx=5)
        self.prompt_selector = ttk.Combobox(prompt_selection_frame, width=60, values=list(self.BENCHMARK_PROMPTS.keys()))
        self.prompt_selector.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.prompt_selector.bind("<<ComboboxSelected>>", self.on_benchmark_prompt_selected)
        
        # Manual Prompt Entry
        prompt_frame = ttk.Frame(config_frame)
        prompt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(prompt_frame, text="Custom Prompt:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=7, width=60, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=5, expand=True)
        self.prompt_text.insert(tk.END, "Write a creative story about a robot who wants to become human.")
        
        # Parameters frame
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Max tokens
        ttk.Label(params_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_tokens_var = tk.StringVar(value="1000")
        ttk.Entry(params_frame, textvariable=self.max_tokens_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Temperature
        ttk.Label(params_frame, text="Temperature:").grid(row=0, column=2, sticky=tk.W, padx=15, pady=5)
        self.temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(params_frame, textvariable=self.temperature_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Number of runs
        ttk.Label(params_frame, text="Number of Runs:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_runs_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.num_runs_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add advanced parameters toggle
        self.advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(params_frame, text="Show Advanced Parameters", variable=self.advanced_var, 
                                         command=self.toggle_advanced_params)
        advanced_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=15, pady=5)
        
        # Advanced parameters frame (initially hidden)
        self.advanced_frame = ttk.Frame(config_frame)
        
        # Token counting
        token_frame = ttk.Frame(self.advanced_frame)
        token_frame.pack(fill=tk.X, pady=5)
        
        self.count_tokens_btn = ttk.Button(token_frame, text="Estimate Token Count", command=self.count_prompt_tokens)
        self.count_tokens_btn.pack(side=tk.LEFT, padx=5)
        
        self.token_count_label = ttk.Label(token_frame, text="Estimated tokens: 0")
        self.token_count_label.pack(side=tk.LEFT, padx=10)
        
        # Run button frame
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Run Test", command=self.run_test, style="Accent.TButton").pack(pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(test_frame, text="Current Test Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom button row
        bottom_button_frame = ttk.Frame(test_frame)
        bottom_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_button_frame, text="Save Results", command=self.save_test_results, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Copy to Clipboard", command=self.copy_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.RIGHT, padx=5)
    
    def toggle_advanced_params(self):
        """Toggle the visibility of advanced parameters."""
        if self.advanced_var.get():
            self.advanced_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.advanced_frame.pack_forget()
    
    def count_prompt_tokens(self):
        """Estimate token count for the current prompt."""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            return
            
        # Simple estimation: 1 token ≈ 4 characters in English
        char_count = len(prompt)
        word_count = len(prompt.split())
        
        # Use both methods for a range
        char_estimate = char_count / 4
        word_estimate = word_count * 1.3
        
        avg_estimate = (char_estimate + word_estimate) / 2
        
        self.token_count_label.config(text=f"Estimated tokens: {int(avg_estimate)}")

    def on_benchmark_prompt_selected(self, event):
        """Handle benchmark prompt selection."""
        selected_prompt = self.prompt_selector.get()
        if selected_prompt in self.BENCHMARK_PROMPTS:
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert(tk.END, self.BENCHMARK_PROMPTS[selected_prompt])
            self.count_prompt_tokens()
    
    def go_to_profiles_tab(self):
        """Switch to the profiles tab."""
        self.notebook.select(0)  # Select the profiles tab (index 0)
    
    def update_profile_selector(self):
        """Update the profile selector dropdown."""
        profile_names = list(self.profiles.keys())
        profile_names.sort()
        self.profile_selector['values'] = profile_names
        
        if profile_names and self.test_profile_var.get() not in profile_names:
            if self.current_profile and self.current_profile in profile_names:
                self.test_profile_var.set(self.current_profile)
                # Only trigger on_profile_selected if UI is ready
                if hasattr(self, 'provider_label'):
                    self.on_profile_selected(None)
            elif profile_names:
                self.test_profile_var.set(profile_names[0])
                # Only trigger on_profile_selected if UI is ready
                if hasattr(self, 'provider_label'):
                    self.on_profile_selected(None)
    
    def on_profile_selected(self, event):
        """Handle profile selection from dropdown."""
        profile_name = self.test_profile_var.get()
        if profile_name in self.profiles:
            self.current_profile = profile_name
            profile = self.profiles[profile_name]
            
            # Make sure UI elements are initialized
            if hasattr(self, 'provider_label'):
                # Update profile info display
                self.provider_label.config(text=f"Provider: {profile.get('provider', 'Unknown')}")
                self.model_label.config(text=f"Model: {profile.get('model', 'Unknown')}")
                self.url_label.config(text=f"API URL: {profile.get('base_url', 'Unknown')}")
                
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
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Create settings sections
        main_frame = ttk.Frame(settings_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App settings
        app_frame = ttk.LabelFrame(main_frame, text="Application Settings")
        app_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme selector
        theme_frame = ttk.Frame(app_frame)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="UI Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.theme_var = tk.StringVar(value="light")
        theme_frame_buttons = ttk.Frame(theme_frame)
        theme_frame_buttons.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(theme_frame_buttons, text="Light", value="light", variable=self.theme_var, 
                      command=self.apply_theme).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(theme_frame_buttons, text="Dark", value="dark", variable=self.theme_var,
                      command=self.apply_theme).pack(side=tk.LEFT, padx=5)
        
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
        
        # Button to apply defaults
        ttk.Button(default_params_frame, text="Apply as Current", 
                 command=self.apply_default_params).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Data management
        data_frame = ttk.LabelFrame(main_frame, text="Data Management")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_frame = ttk.Frame(data_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Export All Results", command=self.export_results).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Import Results", command=self.import_results).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Clear All Results", command=self.clear_all_results).pack(side=tk.LEFT, padx=5, pady=5)
        
        # About section
        about_frame = ttk.LabelFrame(main_frame, text="About")
        about_frame.pack(fill=tk.X, padx=10, pady=10)
        
        about_text = "LLM Performance Tester v1.0.0\n"
        about_text += "A tool for measuring and comparing LLM performance metrics.\n"
        about_text += "Created 2025"
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500)
        about_label.pack(padx=10, pady=10)
    
    def apply_default_params(self):
        """Apply default parameters to current test."""
        try:
            self.max_tokens_var.set(self.default_max_tokens_var.get())
            self.temperature_var.set(self.default_temperature_var.get())
            self.num_runs_var.set(self.default_num_runs_var.get())
            self.update_status("Default parameters applied")
        except Exception as e:
            self.update_status(f"Error applying defaults: {str(e)}", True)
    def create_compare_tab(self):
        """Create the side-by-side comparison tab."""
        compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(compare_frame, text="Compare Models")
        
        # Top section - Profile selectors
        profile_section = ttk.LabelFrame(compare_frame, text="Select Profiles to Compare")
        profile_section.pack(fill=tk.X, padx=10, pady=10)
        
        # First profile selection
        first_profile_frame = ttk.Frame(profile_section)
        first_profile_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(first_profile_frame, text="Profile 1:").pack(side=tk.LEFT, padx=5, pady=5)
        self.profile1_var = tk.StringVar()
        self.profile1_selector = ttk.Combobox(first_profile_frame, textvariable=self.profile1_var, width=40)
        self.profile1_selector.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Second profile selection
        second_profile_frame = ttk.Frame(profile_section)
        second_profile_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(second_profile_frame, text="Profile 2:").pack(side=tk.LEFT, padx=5, pady=5)
        self.profile2_var = tk.StringVar()
        self.profile2_selector = ttk.Combobox(second_profile_frame, textvariable=self.profile2_var, width=40)
        self.profile2_selector.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Initialize profile selectors
        self.update_compare_profile_selectors()
        
        # Profiles info display
        self.compare_info_frame = ttk.Frame(profile_section)
        self.compare_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profile 1 info
        self.profile1_info_frame = ttk.LabelFrame(self.compare_info_frame, text="Profile 1 Info")
        self.profile1_info_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.provider1_label = ttk.Label(self.profile1_info_frame, text="Provider: None")
        self.provider1_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.model1_label = ttk.Label(self.profile1_info_frame, text="Model: None")
        self.model1_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Profile 2 info
        self.profile2_info_frame = ttk.LabelFrame(self.compare_info_frame, text="Profile 2 Info")
        self.profile2_info_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.provider2_label = ttk.Label(self.profile2_info_frame, text="Provider: None")
        self.provider2_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.model2_label = ttk.Label(self.profile2_info_frame, text="Model: None")
        self.model2_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Bind selectors to update info
        self.profile1_selector.bind("<<ComboboxSelected>>", lambda e: self.on_compare_profile_selected(1))
        self.profile2_selector.bind("<<ComboboxSelected>>", lambda e: self.on_compare_profile_selected(2))
        
        # Test configuration
        config_frame = ttk.LabelFrame(compare_frame, text="Test Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Prompt Selection
        prompt_selection_frame = ttk.Frame(config_frame)
        prompt_selection_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        ttk.Label(prompt_selection_frame, text="Benchmark Prompt:").pack(side=tk.LEFT, padx=5)
        self.compare_prompt_selector = ttk.Combobox(prompt_selection_frame, width=60, values=list(self.BENCHMARK_PROMPTS.keys()))
        self.compare_prompt_selector.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.compare_prompt_selector.bind("<<ComboboxSelected>>", self.on_compare_benchmark_prompt_selected)
        
        # Manual Prompt Entry
        prompt_frame = ttk.Frame(config_frame)
        prompt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(prompt_frame, text="Custom Prompt:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.compare_prompt_text = scrolledtext.ScrolledText(prompt_frame, height=7, width=60, wrap=tk.WORD)
        self.compare_prompt_text.pack(fill=tk.X, padx=5, pady=5, expand=True)
        self.compare_prompt_text.insert(tk.END, "Write a creative story about a robot who wants to become human.")
        
        # Parameters frame
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Max tokens
        ttk.Label(params_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.compare_max_tokens_var = tk.StringVar(value="1000")
        ttk.Entry(params_frame, textvariable=self.compare_max_tokens_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Temperature
        ttk.Label(params_frame, text="Temperature:").grid(row=0, column=2, sticky=tk.W, padx=15, pady=5)
        self.compare_temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(params_frame, textvariable=self.compare_temperature_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Number of runs
        ttk.Label(params_frame, text="Number of Runs:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.compare_num_runs_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.compare_num_runs_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Run button frame
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Run Comparison", command=self.run_comparison, style="Accent.TButton").pack(pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(compare_frame, text="Comparison Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabs for text and chart results
        compare_results_notebook = ttk.Notebook(results_frame)
        compare_results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text results tab
        text_results_frame = ttk.Frame(compare_results_notebook)
        compare_results_notebook.add(text_results_frame, text="Text Results")
        
        self.compare_results_text = scrolledtext.ScrolledText(text_results_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.compare_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chart results tab
        chart_results_frame = ttk.Frame(compare_results_notebook)
        compare_results_notebook.add(chart_results_frame, text="Chart")
        
        self.compare_figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.compare_ax = self.compare_figure.add_subplot(111)
        self.compare_chart_canvas = FigureCanvasTkAgg(self.compare_figure, chart_results_frame)
        self.compare_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial plot
        self.compare_ax.set_title('Model Comparison')
        self.compare_ax.set_xlabel('Model')
        self.compare_ax.set_ylabel('Tokens Per Second (TPS)')
        self.compare_ax.text(0.5, 0.5, "Run a comparison to see results", ha='center', va='center', transform=self.compare_ax.transAxes)
        self.compare_chart_canvas.draw()
        
        # Bottom button row
        bottom_button_frame = ttk.Frame(compare_frame)
        bottom_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_button_frame, text="Save Results", command=self.save_comparison_results, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Copy to Clipboard", command=self.copy_comparison_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Clear Results", command=self.clear_comparison_results).pack(side=tk.RIGHT, padx=5)
    
    def update_compare_profile_selectors(self):
        """Update both profile selectors in the comparison tab."""
        # Make sure UI elements are initialized
        if not hasattr(self, 'profile1_selector') or not hasattr(self, 'profile2_selector'):
            return
            
        profile_names = list(self.profiles.keys())
        profile_names.sort()
        
        self.profile1_selector['values'] = profile_names
        self.profile2_selector['values'] = profile_names
        
        if profile_names:
            if not self.profile1_var.get() or self.profile1_var.get() not in profile_names:
                self.profile1_var.set(profile_names[0])
                self.on_compare_profile_selected(1)
                
            if len(profile_names) > 1:
                if not self.profile2_var.get() or self.profile2_var.get() not in profile_names:
                    self.profile2_var.set(profile_names[1])
                    self.on_compare_profile_selected(2)
            elif not self.profile2_var.get() or self.profile2_var.get() not in profile_names:
                self.profile2_var.set(profile_names[0])
                self.on_compare_profile_selected(2)
    
    def on_compare_profile_selected(self, profile_num):
        """Handle profile selection in the comparison tab."""
        # Make sure UI elements are initialized
        if not hasattr(self, 'provider1_label') or not hasattr(self, 'provider2_label'):
            return
            
        if profile_num == 1:
            profile_name = self.profile1_var.get()
            if profile_name in self.profiles:
                profile = self.profiles[profile_name]
                self.provider1_label.config(text=f"Provider: {profile.get('provider', 'Unknown')}")
                self.model1_label.config(text=f"Model: {profile.get('model', 'Unknown')}")
        else:
            profile_name = self.profile2_var.get()
            if profile_name in self.profiles:
                profile = self.profiles[profile_name]
                self.provider2_label.config(text=f"Provider: {profile.get('provider', 'Unknown')}")
                self.model2_label.config(text=f"Model: {profile.get('model', 'Unknown')}")
    
    def on_compare_benchmark_prompt_selected(self, event):
        """Handle benchmark prompt selection in comparison tab."""
        selected_prompt = self.compare_prompt_selector.get()
        if selected_prompt in self.BENCHMARK_PROMPTS:
            self.compare_prompt_text.delete("1.0", tk.END)
            self.compare_prompt_text.insert(tk.END, self.BENCHMARK_PROMPTS[selected_prompt])
    
    def run_comparison(self):
        """Run comparison tests on two selected profiles."""
        profile1_name = self.profile1_var.get()
        profile2_name = self.profile2_var.get()
        
        if not profile1_name or profile1_name not in self.profiles:
            messagebox.showerror("Error", "Please select a valid first profile")
            return
            
        if not profile2_name or profile2_name not in self.profiles:
            messagebox.showerror("Error", "Please select a valid second profile")
            return
        
        profile1 = self.profiles.get(profile1_name)
        profile2 = self.profiles.get(profile2_name)
        
        if not profile1 or not profile2:
            messagebox.showerror("Error", "One or both profiles not found")
            return
        
        # Get test parameters
        prompt = self.compare_prompt_text.get("1.0", tk.END).strip()
        
        try:
            max_tokens = int(self.compare_max_tokens_var.get())
            temperature = float(self.compare_temperature_var.get())
            num_runs = int(self.compare_num_runs_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for max tokens, temperature, and number of runs")
            return
        
        # Clear results text
        self.compare_results_text.config(state=tk.NORMAL)
        self.compare_results_text.delete("1.0", tk.END)
        self.compare_results_text.insert(tk.END, f"Starting comparison between:\n")
        self.compare_results_text.insert(tk.END, f"1. {profile1_name} ({profile1['provider']}, {profile1['model']})\n")
        self.compare_results_text.insert(tk.END, f"2. {profile2_name} ({profile2['provider']}, {profile2['model']})\n")
        self.compare_results_text.insert(tk.END, f"Running {num_runs} tests for each profile...\n\n")
        self.compare_results_text.config(state=tk.DISABLED)
        self.root.update()
        
        # Update status
        self.update_status(f"Running comparison test...")
        
        # Generate a unique ID for this comparison
        self.comparison_id = f"compare_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Run the tests in a separate thread
        thread = threading.Thread(
            target=self.perform_comparison,
            args=(
                self.comparison_id,
                profile1_name, profile1,
                profile2_name, profile2,
                prompt, max_tokens, temperature, num_runs
            )
        )
        thread.daemon = True
        thread.start()
    
    def perform_comparison(self, comparison_id, profile1_name, profile1, profile2_name, profile2, prompt, max_tokens, temperature, num_runs):
        """Perform the comparison tests."""
        # First profile
        self.update_comparison_text(f"Testing profile 1: {profile1_name}...\n")
        profile1_results = self.perform_comparison_test(profile1, prompt, max_tokens, temperature, num_runs)
        
        # Second profile
        self.update_comparison_text(f"\nTesting profile 2: {profile2_name}...\n")
        profile2_results = self.perform_comparison_test(profile2, prompt, max_tokens, temperature, num_runs)
        
        # Calculate averages
        if profile1_results and profile2_results:
            avg_tps1 = sum(result["tps"] for result in profile1_results) / len(profile1_results)
            avg_tps2 = sum(result["tps"] for result in profile2_results) / len(profile2_results)
            
            # Determine winner
            if avg_tps1 > avg_tps2:
                winner = f"{profile1_name} ({profile1['model']})"
                winner_tps = avg_tps1
                loser = f"{profile2_name} ({profile2['model']})"
                loser_tps = avg_tps2
            else:
                winner = f"{profile2_name} ({profile2['model']})"
                winner_tps = avg_tps2
                loser = f"{profile1_name} ({profile1['model']})"
                loser_tps = avg_tps1
            
            difference = abs(avg_tps1 - avg_tps2)
            percent_diff = (difference / min(avg_tps1, avg_tps2)) * 100
            
            summary = f"\n=== COMPARISON SUMMARY ===\n"
            summary += f"{profile1_name} ({profile1['model']}): {avg_tps1:.2f} TPS\n"
            summary += f"{profile2_name} ({profile2['model']}): {avg_tps2:.2f} TPS\n\n"
            summary += f"Winner: {winner} with {winner_tps:.2f} TPS\n"
            summary += f"Difference: {difference:.2f} TPS ({percent_diff:.1f}% faster)\n"
            
            self.update_comparison_text(summary)
            
            # Store the comparison result
            comparison_result = {
                "id": comparison_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "num_runs": num_runs,
                "profile1": {
                    "name": profile1_name,
                    "provider": profile1['provider'],
                    "model": profile1['model'],
                    "results": profile1_results,
                    "avg_tps": avg_tps1
                },
                "profile2": {
                    "name": profile2_name,
                    "provider": profile2['provider'],
                    "model": profile2['model'],
                    "results": profile2_results,
                    "avg_tps": avg_tps2
                },
                "winner": {
                    "name": winner,
                    "tps": winner_tps
                },
                "difference": {
                    "absolute": difference,
                    "percent": percent_diff
                }
            }
            
            # Store for later saving
            self.current_comparison_result = comparison_result
            
            # Update the chart
            self.update_comparison_chart(
                [profile1['model'], profile2['model']],
                [avg_tps1, avg_tps2],
                [profile1['provider'], profile2['provider']]
            )
            
            self.update_status(f"Comparison completed")
        else:
            self.update_comparison_text("\nComparison failed - one or both tests had no valid results")
            self.update_status("Comparison failed", True)
    
    def perform_comparison_test(self, profile, prompt, max_tokens, temperature, num_runs):
        """Run test for a profile during comparison."""
        base_url = profile.get("base_url", "")
        api_key = profile["api_key"]
        model = profile["model"]
        provider = profile["provider"]
        content_type = profile.get("content_type", "application/json")
        additional_headers = profile.get("additional_headers", {})
        
        # Construct the appropriate API endpoint URL based on provider
        if provider == "OpenAI" or provider == "OpenRouter":
            api_url = f"{base_url.rstrip('/')}/chat/completions"
        elif provider == "Anthropic":
            api_url = f"{base_url.rstrip('/')}/messages"
        else:  # Custom provider - assume chat completions
            api_url = f"{base_url.rstrip('/')}/chat/completions"
        
        # Prepare headers
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Bearer {api_key}"
        }
        headers.update(additional_headers)
        
        results = []
        
        for i in range(num_runs):
            self.update_comparison_text(f"Run {i+1}/{num_runs}...\n")
            
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
                    self.update_comparison_text(error_msg)
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
                    "tps": tps
                })
                
                result_text = f"Run {i+1} completed: {tokens_generated:.0f} tokens in {duration:.2f}s = {tps:.2f} TPS\n"
                self.update_comparison_text(result_text)
                
            except Exception as e:
                error_text = f"Error in run {i+1}: {str(e)}\n"
                self.update_comparison_text(error_text)
        
        return results
    
    def update_comparison_text(self, text):
        """Update the comparison results text widget from any thread."""
        self.root.after(0, self._update_comparison_text, text)
    
    def _update_comparison_text(self, text):
        """Update the comparison results text widget (must be called from main thread)."""
        self.compare_results_text.config(state=tk.NORMAL)
        self.compare_results_text.insert(tk.END, text)
        self.compare_results_text.see(tk.END)
        self.compare_results_text.config(state=tk.DISABLED)
    
    def update_comparison_chart(self, models, tps_values, providers):
        """Update the comparison chart with results."""
        self.root.after(0, self._update_comparison_chart, models, tps_values, providers)
    
    def _update_comparison_chart(self, models, tps_values, providers):
        """Update the comparison chart (must be called from main thread)."""
        # Clear the chart
        self.compare_ax.clear()
        
        # Create x positions
        x_pos = [0, 1]
        
        # Define colors based on provider
        colors = []
        for provider in providers:
            if provider == "OpenAI":
                colors.append('#74aa9c')  # OpenAI green
            elif provider == "Anthropic":
                colors.append('#b33e95')  # Anthropic purple
            elif provider == "OpenRouter":
                colors.append('#f28c28')  # OpenRouter orange
            else:
                colors.append('#3498db')  # Default blue
        
        # Create the bar chart
        bars = self.compare_ax.bar(x_pos, tps_values, color=colors)
        
        # Add labels
        self.compare_ax.set_xlabel('Model')
        self.compare_ax.set_ylabel('Tokens Per Second (TPS)')
        self.compare_ax.set_title('Model Performance Comparison')
        self.compare_ax.set_xticks(x_pos)
        self.compare_ax.set_xticklabels(models)
        
        # Add grid lines for better readability
        self.compare_ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.compare_ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{height:.2f}', ha='center', va='bottom')
        
        # Add a legend for providers
        self.compare_ax.legend(providers)
        
        # Adjust layout
        self.compare_figure.tight_layout()
        
        # Redraw the canvas
        self.compare_chart_canvas.draw()
    
    def save_comparison_results(self):
        """Save the current comparison results."""
        if not hasattr(self, 'current_comparison_result') or not self.current_comparison_result:
            messagebox.showerror("Error", "No comparison results to save")
            return
        
        # Add the result to the stored test results
        result_id = self.current_comparison_result["id"]
        self.test_results[result_id] = self.current_comparison_result
        self.save_test_results_to_file()
        
        # Update the results listbox
        self.update_results_listbox()
        
        messagebox.showinfo("Success", "Comparison results saved successfully")
        self.update_status("Comparison results saved successfully")
    
    def copy_comparison_results(self):
        """Copy comparison results to clipboard."""
        if not hasattr(self, 'current_comparison_result') or not self.current_comparison_result:
            messagebox.showerror("Error", "No comparison results to copy")
            return
        
        try:
            result_text = self.compare_results_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(result_text)
            self.update_status("Comparison results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
    
    def clear_comparison_results(self):
        """Clear the comparison results text."""
        self.compare_results_text.config(state=tk.NORMAL)
        self.compare_results_text.delete("1.0", tk.END)
        self.compare_results_text.config(state=tk.DISABLED)
        
        # Clear the chart
        self.compare_ax.clear()
        self.compare_ax.set_title('Model Comparison')
        self.compare_ax.set_xlabel('Model')
        self.compare_ax.set_ylabel('Tokens Per Second (TPS)')
        self.compare_ax.text(0.5, 0.5, "Run a comparison to see results", ha='center', va='center', transform=self.compare_ax.transAxes)
        self.compare_chart_canvas.draw()
        
        if hasattr(self, 'current_comparison_result'):
            delattr(self, 'current_comparison_result')
        self.update_status("Comparison results cleared")
    
    def apply_theme(self):
        """Apply the selected theme."""
        theme = self.theme_var.get()
        sv_ttk.set_theme(theme)
        self.update_status(f"Theme updated to {theme}")
    
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
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Compare Results")
        
        # Split into two frames
        top_frame = ttk.LabelFrame(results_frame, text="Saved Tests")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        bottom_frame = ttk.LabelFrame(results_frame, text="Comparison Chart")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - Results selection
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.results_filter_var = tk.StringVar()
        results_filter_entry = ttk.Entry(filter_frame, textvariable=self.results_filter_var)
        results_filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.results_filter_var.trace("w", lambda name, index, mode: self.update_results_listbox())
        
        # Results listbox with scrollbar
        list_frame = ttk.Frame(top_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_listbox = tk.Listbox(list_frame, height=8, selectmode=tk.MULTIPLE)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.results_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_results_listbox()
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Button(btn_frame, text="Compare Selected", command=self.compare_results, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Selected", command=self.export_selected_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Show Details", command=self.show_result_details).pack(side=tk.LEFT, padx=5)
        
        # Bottom frame - Comparison display
        chart_frame = ttk.Frame(bottom_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial plot
        self.ax.set_title('LLM Performance Comparison')
        self.ax.set_xlabel('Model')
        self.ax.set_ylabel('Tokens Per Second (TPS)')
        self.ax.text(0.5, 0.5, "Select results to compare", ha='center', va='center', transform=self.ax.transAxes)
        self.chart_canvas.draw()
    
    def show_result_details(self):
        """Show detailed information for selected result."""
        selected = self.results_listbox.curselection()
        
        if not selected or len(selected) != 1:
            messagebox.showinfo("Info", "Please select exactly one result to view details")
            return
        
        # Get the selected result
        sorted_results = sorted(
            self.test_results.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        if selected[0] < len(sorted_results):
            result_id = sorted_results[selected[0]][0]
            result = self.test_results[result_id]
            
            # Create a details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Result Details: {result.get('model', 'Unknown')}")
            details_window.geometry("600x500")
            
            # Apply theme
            if hasattr(self, 'theme_var'):
                sv_ttk.set_theme(self.theme_var.get())
            
            # Create content
            content_frame = ttk.Frame(details_window, padding=10)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Basic info
            info_frame = ttk.LabelFrame(content_frame, text="Test Information", padding=10)
            info_frame.pack(fill=tk.X, pady=5)
            
            info_text = f"Timestamp: {result.get('timestamp', 'Unknown')}\n"
            info_text += f"Provider: {result.get('provider', 'Unknown')}\n"
            info_text += f"Model: {result.get('model', 'Unknown')}\n"
            info_text += f"Average TPS: {result.get('avg_tps', 0):.2f}\n"
            info_text += f"Max Tokens: {result.get('max_tokens', 0)}\n"
            info_text += f"Temperature: {result.get('temperature', 0)}"
            
            ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
            
            # Run details
            runs_frame = ttk.LabelFrame(content_frame, text="Individual Runs", padding=10)
            runs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            runs_text = scrolledtext.ScrolledText(runs_frame, wrap=tk.WORD)
            runs_text.pack(fill=tk.BOTH, expand=True)
            
            for run in result.get('runs', []):
                run_text = f"Run {run.get('run', '?')}: {run.get('tokens_generated', 0):.0f} tokens in "
                run_text += f"{run.get('duration', 0):.2f}s = {run.get('tps', 0):.2f} TPS\n"
                runs_text.insert(tk.END, run_text)
            
            # Prompt used
            prompt_frame = ttk.LabelFrame(content_frame, text="Prompt Used", padding=10)
            prompt_frame.pack(fill=tk.X, pady=5)
            
            prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=6)
            prompt_text.pack(fill=tk.BOTH)
            prompt_text.insert(tk.END, result.get('prompt', 'No prompt data available'))
            
            # Close button
            ttk.Button(content_frame, text="Close", command=details_window.destroy).pack(pady=10)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                             background="#ffffe0", relief="solid", borderwidth=1,
                             font=("TkDefaultFont", "8"))
            label.pack(ipadx=5, ipady=2)
            
            widget.tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def toggle_model_entry_mode(self):
        """Toggle between dropdown and manual entry for model selection."""
        current_mode = self.model_entry_mode.get()
        current_value = self.model_var.get()
        
        if current_mode == "dropdown":
            # Switch to manual entry
            self.model_combo.pack_forget()
            self.model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.model_entry_mode.set("manual")
            self.toggle_model_entry_btn.config(text="📋")
            self.create_tooltip(self.toggle_model_entry_btn, "Switch to dropdown selection")
            self.model_status_label.config(text="Manual model entry mode")
        else:
            # Switch to dropdown
            self.model_entry.pack_forget()
            self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.model_entry_mode.set("dropdown")
            self.toggle_model_entry_btn.config(text="📝")
            self.create_tooltip(self.toggle_model_entry_btn, "Switch to manual entry")
            self.model_status_label.config(text="Dropdown selection mode")
        
        # Preserve the value
        self.model_var.set(current_value)
    
    def update_api_url(self, event):
        """Update the API URL based on the provider selection."""
        provider = self.provider_var.get()
        
        if provider == "OpenAI":
            self.base_url_var.set("https://api.openai.com/v1")
            self.model_var.set("gpt-3.5-turbo")
            self.content_type_var.set("application/json")
            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert(tk.END, '{}')
            # Update model combobox if we have OpenAI models cached
            if "OpenAI" in self.available_models:
                self.model_combo['values'] = self.available_models["OpenAI"]
                # Switch to dropdown mode
                if self.model_entry_mode.get() == "manual":
                    self.toggle_model_entry_mode()
            else:
                # Auto-fetch models if we have an API key
                if self.api_key_var.get():
                    self.model_status_label.config(text="Fetching OpenAI models...")
                    self.fetch_models()
                
        elif provider == "Anthropic":
            self.base_url_var.set("https://api.anthropic.com/v1")
            self.model_var.set("claude-3-opus-20240229")
            self.content_type_var.set("application/json")
            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert(tk.END, '{"anthropic-version": "2023-06-01"}')
            # Update model combobox if we have Anthropic models cached
            if "Anthropic" in self.available_models:
                self.model_combo['values'] = self.available_models["Anthropic"]
                # Switch to dropdown mode
                if self.model_entry_mode.get() == "manual":
                    self.toggle_model_entry_mode()
            else:
                # For Anthropic, we'll use a predefined list
                self.model_status_label.config(text="Using built-in Anthropic models list")
                self.fetch_models()
                
        elif provider == "OpenRouter":
            self.base_url_var.set("https://router.requesty.ai/v1")
            self.model_var.set("openai/gpt-3.5-turbo")
            self.content_type_var.set("application/json")
            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert(tk.END, '{"HTTP-Referer": "localhost"}')
            # Update model combobox if we have OpenRouter models cached
            if "OpenRouter" in self.available_models:
                self.model_combo['values'] = self.available_models["OpenRouter"]
                # Switch to dropdown mode
                if self.model_entry_mode.get() == "manual":
                    self.toggle_model_entry_mode()
            else:
                # Auto-fetch models if we have an API key
                if self.api_key_var.get():
                    self.model_status_label.config(text="Fetching OpenRouter models...")
                    self.fetch_models()
        else:
            # For Custom provider, switch to manual entry mode
            if self.model_entry_mode.get() == "dropdown":
                self.toggle_model_entry_mode()
            self.model_status_label.config(text="Using manual model entry for custom provider")
        
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
        
        filter_text = self.filter_var.get().lower() if hasattr(self, 'filter_var') else ""
        
        for profile_name in profile_names:
            # Apply filter if there is one
            if filter_text and filter_text not in profile_name.lower():
                continue
                
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
            if not messagebox.askyesno("Warning", "API Key is empty. Save anyway?"):
                return
        
        # Get additional headers
        try:
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            additional_headers = json.loads(headers_text) if headers_text else {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in additional headers")
            return
        
        # Create profile
        profile = {
            "provider": self.provider_var.get(),
            "base_url": self.base_url_var.get(),
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "content_type": self.content_type_var.get(),
            "additional_headers": additional_headers
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
            self.base_url_var.set(profile.get("base_url", ""))
            self.api_key_var.set(profile.get("api_key", ""))
            self.model_var.set(profile.get("model", ""))
            self.content_type_var.set(profile.get("content_type", "application/json"))
            
            # Set additional headers
            self.headers_text.delete("1.0", tk.END)
            additional_headers = profile.get("additional_headers", {})
            self.headers_text.insert(tk.END, json.dumps(additional_headers, indent=4))
            
            self.update_status(f"Loaded profile '{profile_name}' for editing")
        else:
            # Set as current profile for testing
            self.current_profile = profile_name
            
            # Update profile info in test tab
            self.test_profile_var.set(profile_name)
            self.provider_label.config(text=f"Provider: {profile.get('provider', 'Unknown')}")
            self.model_label.config(text=f"Model: {profile.get('model', 'Unknown')}")
            self.url_label.config(text=f"API URL: {profile.get('chat_url', profile.get('api_url', 'Unknown'))}")
            
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
        base_url = profile.get("base_url", "")
        api_key = profile["api_key"]
        model = profile["model"]
        provider = profile["provider"]
        content_type = profile.get("content_type", "application/json")
        additional_headers = profile.get("additional_headers", {})
        
        # Construct the appropriate API endpoint URL based on provider
        if provider == "OpenAI" or provider == "OpenRouter":
            api_url = f"{base_url.rstrip('/')}/chat/completions"
        elif provider == "Anthropic":
            api_url = f"{base_url.rstrip('/')}/messages"
        else:  # Custom provider - assume chat completions
            api_url = f"{base_url.rstrip('/')}/chat/completions"
        
        # Prepare headers
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Bearer {api_key}"
        }
        headers.update(additional_headers)
        
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
        
        filter_text = self.results_filter_var.get().lower() if hasattr(self, 'results_filter_var') else ""
        
        for result_id, result in sorted_results:
            # Apply filter if there is one
            model_info = f"{result.get('provider', '')}-{result.get('model', '')}"
            if filter_text and filter_text not in model_info.lower() and filter_text not in result_id.lower():
                continue
                
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