import google.generativeai as genai
import tkinter as tk
from tkinter import ttk
import threading
import re
import textwrap

# --- Configure the Gemini API (Replace your API key) ---
genai.configure(api_key="AIzaSyAZUAvpnrnw83XAACsXacZ_xqdsPWf3CTw")

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1000,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=[],
)

convo = model.start_chat(history=[])

# --- Beautify Text Function ---
def beautify_text(text):
    text = text.replace("*", "")
    text = text.strip()

    # Preserve code blocks
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
    for i, block in enumerate(code_blocks):
        text = text.replace(f"```{block}```", f"__CODE_BLOCK_{i}__")

    # Add newlines after options like A), B), 1., 2.
    text = re.sub(r'(?<!\n)([A-D]\))', r'\n\1', text)
    text = re.sub(r'(?<!\n)(\d+\.)', r'\n\1', text)

    # Add newlines after bullets
    text = re.sub(r'(?<!\n)([*•-])', r'\n\1', text)

    # Fix multiple newlines into one
    text = re.sub(r'\n+', '\n', text)

    # Wrap paragraphs
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not re.match(r"^(\d+\.)|([A-D]\))|([-*•])", line):
            line = textwrap.fill(line, width=80)
        lines.append(line)

    text = "\n".join(lines)

    # Bring back code blocks
    for i, block in enumerate(code_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", f"```{block}```")

    return text

# --- Typing Animation ---
def type_text(widget, text):
    widget.config(state='normal')
    widget.insert(tk.END, "AI is thinking...\n")
    widget.update()
    widget.delete("end-2l", tk.END)  # Remove "AI is thinking..." after typing starts

    for char in text:
        widget.insert(tk.END, char)
        widget.see(tk.END)
        widget.update()
        widget.after(10)  # Typing speed (reduced for 2x faster typing)
    
    widget.insert(tk.END, "\n\n")
    widget.config(state='disabled')

# --- Send Message ---
def send_message():
    user_input = user_entry.get()
    if user_input.strip() == "":
        return
    
    chat_log.config(state='normal')
    chat_log.insert(tk.END, f"You: {user_input}\n\n")
    chat_log.config(state='disabled')

    user_entry.delete(0, tk.END)

    def run():
        response = convo.send_message(user_input)
        beautified_text = beautify_text(convo.last.text)
        type_text(chat_log, f"AI: {beautified_text}")

    threading.Thread(target=run).start()

# --- Toggle Dark Mode ---
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg_color = "#1e1e1e" if dark_mode else "#ffffff"
    fg_color = "#ffffff" if dark_mode else "#000000"
    entry_bg = "#2d2d2d" if dark_mode else "#f0f0f0"
    
    root.config(bg=bg_color)
    chat_frame.config(bg=bg_color)
    chat_log.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    user_entry.config(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    send_button.config(bg="#4CAF50" if dark_mode else "#0078D7", fg="white")
    dark_mode_button.config(bg="#555555" if dark_mode else "#dddddd", fg="white" if dark_mode else "black")

# --- Setup GUI ---
root = tk.Tk()
root.title("AI Chatbot")
root.geometry("600x700")
root.configure(bg="#ffffff")
dark_mode = False

# Chat Log
chat_frame = tk.Frame(root, bg="#ffffff")
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_log = tk.Text(chat_frame, wrap=tk.WORD, state='disabled', bg="#ffffff", fg="#000000", font=("Helvetica", 12))
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# User Entry
user_entry = tk.Entry(root, font=("Helvetica", 14), bg="#f0f0f0")
user_entry.pack(padx=10, pady=10, fill=tk.X)

# Buttons Frame
buttons_frame = tk.Frame(root, bg="#ffffff")
buttons_frame.pack(padx=10, pady=10, fill=tk.X)

send_button = tk.Button(buttons_frame, text="Send", command=send_message, font=("Helvetica", 12), bg="#0078D7", fg="white")
send_button.pack(side=tk.LEFT, padx=(0, 10))

dark_mode_button = tk.Button(buttons_frame, text="🌙 Toggle Dark Mode", command=toggle_dark_mode, font=("Helvetica", 12), bg="#dddddd", fg="black")
dark_mode_button.pack(side=tk.LEFT)

# Run App
root.mainloop()



# client = genai.Client(api_key="AIzaSyAZUAvpnrnw83XAACsXacZ_xqdsPWf3CTw")

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Explain how AI works",
# )

# print(response.text)