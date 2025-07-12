import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import threading
from collections import deque


class Maze:
    def __init__(self, file_path=None):
        """Initialize the maze from a file or create empty maze"""
        self.horizontal_walls = []
        self.vertical_walls = []
        self.entrance = None
        self.exit = None
        self.rows = 0
        self.cols = 0

        if file_path:
            self.parse_maze_file(file_path)
        else:
            self.create_empty_maze(8, 8)  # Default size

    def create_empty_maze(self, rows, cols):
        """Create an empty maze with given dimensions"""
        self.rows = rows
        self.cols = cols
        # Initialize all walls as False (no walls initially)
        self.horizontal_walls = [[False for _ in range(cols)] for _ in range(rows + 1)]
        self.vertical_walls = [[False for _ in range(cols + 1)] for _ in range(rows)]

        # Set border walls
        for j in range(cols):
            self.horizontal_walls[0][j] = True  # Top border
            self.horizontal_walls[rows][j] = True  # Bottom border

        for i in range(rows):
            self.vertical_walls[i][0] = True  # Left border
            self.vertical_walls[i][cols] = True  # Right border

        self.entrance = (0, 0)
        self.exit = (rows - 1, cols - 1)

    def parse_maze_file(self, file_path):
        """Parse the maze text file and extract walls and coordinates"""
        with open(file_path, 'r') as file:
            lines = [line.rstrip() for line in file.readlines()]

        # Find where the coordinates start
        coord_start_idx = 0
        for i, line in enumerate(lines):
            if ',' in line:
                coord_start_idx = i
                break

        wall_lines = lines[:coord_start_idx]

        # Count the number of horizontal wall lines (should be rows + 1)
        # Each pair of lines (horizontal, vertical) represents one row, plus the last horizontal line
        self.rows = (len(wall_lines) + 1) // 2 - 1 if len(wall_lines) % 2 != 0 else len(wall_lines) // 2

        # Determine cols based on max horizontal wall line length or vertical wall line length
        # A horizontal line has 'cols' walls separated by 'cols-1' spaces.
        # A vertical line has 'cols+1' walls separated by 'cols' spaces.
        # So, the number of elements in a horizontal wall line (including spaces) is 2*cols - 1
        # The number of elements in a vertical wall line (including spaces) is 2*cols + 1

        max_line_len = 0
        if wall_lines:
            # Let's find max width by checking elements in a horizontal wall line (elements are '-' or ' ')
            # Example: - - - - (4 elements) -> cols = 4
            # Example: | | | | | (5 elements) -> cols + 1 = 5 -> cols = 4
            if len(wall_lines[0].split()) > 0:  # Check if the first line is not empty
                self.cols = len(wall_lines[0].split())  # Assuming first line is horizontal wall representation
                # Adjust for horizontal wall lines that might have fewer elements than self.cols
                # Example: '- - -' length is 3, means 3 horizontal walls, so 3 columns
                # The length of a horizontal wall line string is `2*cols - 1` if it has spaces
                # If parsed by split() and elements are only '-' or ' ', it's `cols` elements
                if len(wall_lines) > 1 and len(wall_lines[1].split()) > 0:  # Check vertical walls as well for cols
                    self.cols = max(self.cols, len(wall_lines[1].split()) - 1)  # Vertical walls have cols+1 elements
            elif len(wall_lines) > 1 and len(wall_lines[1].split()) > 0:
                self.cols = len(wall_lines[1].split()) - 1  # Vertical walls have cols+1 elements

        # Fallback if no wall lines provide column info (e.g., empty maze file)
        if self.cols == 0 and self.rows > 0:
            self.cols = 1  # A single column maze

        # Initialize walls
        self.horizontal_walls = [[False for _ in range(self.cols)] for _ in range(self.rows + 1)]
        self.vertical_walls = [[False for _ in range(self.cols + 1)] for _ in range(self.rows)]

        # Parse walls
        for i, line in enumerate(wall_lines):
            elements = line.split()
            if i % 2 == 0:  # Horizontal walls
                row = i // 2
                for j, element in enumerate(elements):
                    if j < self.cols and element == '-':
                        self.horizontal_walls[row][j] = True
            else:  # Vertical walls
                row = i // 2
                for j, element in enumerate(elements):
                    if j < self.cols + 1 and element == '|':  # It should be self.cols + 1 for vertical
                        self.vertical_walls[row][j] = True

        # Parse entrance and exit
        entrance_line = lines[coord_start_idx].strip()
        exit_line = lines[coord_start_idx + 1].strip()
        self.entrance = tuple(map(int, entrance_line.split(',')))
        self.exit = tuple(map(int, exit_line.split(',')))

    def has_wall_between(self, cell1, cell2):
        """Check if there is a wall between two adjacent cells"""
        row1, col1 = cell1
        row2, col2 = cell2

        # Check if cells are adjacent
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return True  # Not adjacent cells

        # Check horizontal walls
        if row1 + 1 == row2:  # cell2 is below cell1
            return self.horizontal_walls[row1 + 1][col1]
        elif row2 + 1 == row1:  # cell2 is above cell1
            return self.horizontal_walls[row1][col1]

        # Check vertical walls
        if col1 + 1 == col2:  # cell2 is to the right of cell1
            return self.vertical_walls[row1][col1 + 1]
        elif col2 + 1 == col1:  # cell2 is to the left of cell1
            return self.vertical_walls[row1][col1]

        return False

    def get_valid_moves(self, cell):
        """Get all valid moves from the current cell (up, left, down, right)"""
        row, col = cell
        possible_moves = []

        # Check in the specific order: up, left, down, right (as specified in the assignment)
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        direction_names = ["up", "left", "down", "right"]

        for (dr, dc), direction in zip(directions, direction_names):
            new_row, new_col = row + dr, col + dc

            # Check if the new position is within the maze boundaries
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                # Check if there's no wall between the current cell and the new cell
                if not self.has_wall_between((row, col), (new_row, new_col)):
                    possible_moves.append(((new_row, new_col), direction))

        return possible_moves

    def is_exit(self, cell):
        """Check if the cell is the exit"""
        return cell == self.exit

    def save_to_file(self, file_path):
        """Save the maze to a text file in the required format"""
        with open(file_path, 'w') as file:
            # Write horizontal walls (rows + 1 lines)
            for i in range(self.rows + 1):
                line_elements = []
                for j in range(self.cols):
                    line_elements.append("-" if self.horizontal_walls[i][j] else " ")
                file.write(" ".join(line_elements) + "\n")

                # Write vertical walls for the current row (rows lines)
                if i < self.rows:
                    line_elements = []
                    for j in range(self.cols + 1):
                        line_elements.append("|" if self.vertical_walls[i][j] else " ")
                    file.write(" ".join(line_elements) + "\n")

            # Write entrance and exit coordinates
            file.write(f"{self.entrance[0]},{self.entrance[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")


class MazeSolver:
    def __init__(self, maze):
        """Initialize the maze solver with a maze object"""
        self.maze = maze
        self.path = []
        self.visited = set()
        self.steps_taken = 0
        self.exploration_order = []  # For step-by-step visualization
        self.solve_time = 0.0

    def dfs(self, step_by_step=False):
        """Find a path using Depth-First Search (LIFO stack)"""
        start_time = time.time()
        self.visited = set()
        self.path = []
        self.steps_taken = 0
        self.exploration_order = []

        stack = [(self.maze.entrance, [])]

        while stack:
            current, path = stack.pop()  # LIFO
            self.steps_taken += 1

            if current in self.visited:
                continue

            self.visited.add(current)
            if step_by_step:
                self.exploration_order.append(('visit', current))

            if self.maze.is_exit(current):
                self.path = path + [current]
                self.solve_time = time.time() - start_time
                return True

            valid_moves = self.maze.get_valid_moves(current)
            valid_moves.reverse()  # For correct order when using stack (pop simulates DFS LIFO)

            for next_cell, _ in valid_moves:
                if next_cell not in self.visited:
                    stack.append((next_cell, path + [current]))
                    if step_by_step:
                        self.exploration_order.append(('explore', next_cell))

        self.solve_time = time.time() - start_time
        return False

    def bfs(self, step_by_step=False):
        """Find a path using Breadth-First Search (FIFO queue)"""
        start_time = time.time()
        self.visited = set()
        self.path = []
        self.steps_taken = 0
        self.exploration_order = []

        queue = deque([(self.maze.entrance, [])])

        while queue:
            current, path = queue.popleft()  # FIFO
            self.steps_taken += 1

            if current in self.visited:
                continue

            self.visited.add(current)
            if step_by_step:
                self.exploration_order.append(('visit', current))

            if self.maze.is_exit(current):
                self.path = path + [current]
                self.solve_time = time.time() - start_time
                return True

            valid_moves = self.maze.get_valid_moves(current)

            for next_cell, _ in valid_moves:
                if next_cell not in self.visited:
                    queue.append((next_cell, path + [current]))
                    if step_by_step:
                        self.exploration_order.append(('explore', next_cell))

        self.solve_time = time.time() - start_time
        return False

    def get_path_length(self):
        """Return the length of the discovered path"""
        if not self.path:
            return 0
        return len(self.path) - 1


class MazeVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Maze Solver Visualization")
        self.master.geometry("1200x800")

        self.maze = None
        self.solver = None
        self.cell_size = 30
        self.animation_speed = 100  # ms between steps
        self.is_editing = False
        self.edit_mode = "wall"  # "wall", "entrance", "exit"

        self.animation_thread = None  # To hold the animation thread
        self.animation_stop_event = threading.Event()  # Event to signal stopping animation

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="File Operations")
        file_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(file_frame, text="Load Maze", command=self.load_maze).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Save Maze", command=self.save_maze).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="New Maze", command=self.create_new_maze).pack(side=tk.LEFT, padx=5)

        # Algorithm controls
        algo_frame = ttk.LabelFrame(control_frame, text="Algorithm Controls")
        algo_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(algo_frame, text="Solve DFS", command=self.solve_dfs_threaded).pack(side=tk.LEFT, padx=5)
        ttk.Button(algo_frame, text="Solve BFS", command=self.solve_bfs_threaded).pack(side=tk.LEFT, padx=5)
        ttk.Button(algo_frame, text="Compare Both", command=self.compare_algorithms_threaded).pack(side=tk.LEFT, padx=5)
        ttk.Button(algo_frame, text="Clear Solution", command=self.clear_solution).pack(side=tk.LEFT, padx=5)

        # Animation controls
        anim_frame = ttk.LabelFrame(control_frame, text="Animation Controls")
        anim_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(anim_frame, text="Step-by-Step DFS", command=self.animate_dfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(anim_frame, text="Step-by-Step BFS", command=self.animate_bfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(anim_frame, text="Stop Animation", command=self.stop_animation).pack(side=tk.LEFT,
                                                                                        padx=5)  # New Stop Button

        ttk.Label(anim_frame, text="Speed (ms):").pack(side=tk.LEFT, padx=(20, 0))
        self.speed_var = tk.IntVar(value=100)
        speed_scale = ttk.Scale(anim_frame, from_=10, to=500, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.LEFT, padx=5)

        # Editing controls
        edit_frame = ttk.LabelFrame(control_frame, text="Maze Editor")
        edit_frame.pack(fill=tk.X, pady=(0, 5))

        self.edit_var = tk.BooleanVar()
        ttk.Checkbutton(edit_frame, text="Edit Mode", variable=self.edit_var,
                        command=self.toggle_edit_mode).pack(side=tk.LEFT, padx=5)

        self.mode_var = tk.StringVar(value="wall")
        ttk.Radiobutton(edit_frame, text="Walls", variable=self.mode_var,
                        value="wall").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(edit_frame, text="Entrance", variable=self.mode_var,
                        value="entrance").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(edit_frame, text="Exit", variable=self.mode_var,
                        value="exit").pack(side=tk.LEFT, padx=5)

        # Results display
        self.results_frame = ttk.LabelFrame(control_frame, text="Results")
        self.results_frame.pack(fill=tk.X)

        self.results_text = tk.Text(self.results_frame, height=4, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for maze display
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='white', scrollregion=(0, 0, 1000, 1000))

        # Scrollbars for canvas
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

    def stop_animation(self):
        """Stops any ongoing animation."""
        self.animation_stop_event.set()
        self.update_results("Animation stopped.")

    def load_maze(self):
        """Load a maze from file"""
        file_path = filedialog.askopenfilename(
            title="Select Maze File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.stop_animation()  # Stop any ongoing animation
                self.maze = Maze(file_path)
                self.draw_maze()
                self.update_results("Maze loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load maze: {str(e)}")

    def save_maze(self):
        """Save the current maze to file"""
        if not self.maze:
            messagebox.showwarning("Warning", "No maze to save!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Maze As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.maze.save_to_file(file_path)
                self.update_results("Maze saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save maze: {str(e)}")

    def create_new_maze(self):
        """Create a new empty maze"""
        dialog = tk.Toplevel(self.master)
        dialog.title("New Maze")
        dialog.geometry("300x180")  # Increased height for better layout
        dialog.transient(self.master)
        dialog.grab_set()

        ttk.Label(dialog, text="Rows:").pack(pady=5)
        rows_var = tk.IntVar(value=8)
        rows_entry = ttk.Entry(dialog, textvariable=rows_var)
        rows_entry.pack(pady=5)

        ttk.Label(dialog, text="Columns:").pack(pady=5)
        cols_var = tk.IntVar(value=8)
        cols_entry = ttk.Entry(dialog, textvariable=cols_var)
        cols_entry.pack(pady=5)

        def create_maze_action():
            try:
                rows = rows_var.get()
                cols = cols_var.get()
                if rows <= 0 or cols <= 0:
                    messagebox.showerror("Input Error", "Rows and columns must be positive integers.")
                    return
                self.stop_animation()  # Stop any ongoing animation
                self.maze = Maze()
                self.maze.create_empty_maze(rows, cols)
                self.draw_maze()
                self.update_results(f"New {rows}x{cols} maze created!")
                dialog.destroy()
            except tk.TclError:  # Catch non-integer input
                messagebox.showerror("Input Error", "Please enter valid integers for rows and columns.")

        ttk.Button(dialog, text="Create", command=create_maze_action).pack(pady=10)
        # Center the dialog
        dialog.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{int(x)}+{int(y)}")

    def solve_dfs_threaded(self):
        """Solve maze using DFS in a separate thread"""
        if not self.maze:
            messagebox.showwarning("Warning", "Please load a maze first!")
            return

        self.stop_animation()  # Stop any ongoing animation
        self.clear_solution()
        self.update_results("Solving with DFS...")

        def run_dfs():
            self.solver = MazeSolver(self.maze)
            found = self.solver.dfs()
            # Schedule the GUI update back on the main thread
            self.master.after(1, lambda: self._post_solve_dfs(found))

        threading.Thread(target=run_dfs, daemon=True).start()  # daemon=True ensures thread exits with main app

    def _post_solve_dfs(self, found):
        if found:
            self.draw_solution("DFS", "red")
            self.update_results(f"DFS Solution - Path Length: {self.solver.get_path_length()}, "
                                f"Steps Explored: {self.solver.steps_taken}, "
                                f"Time: {self.solver.solve_time:.4f}s")
        else:
            self.update_results("DFS: No solution found!")

    def solve_bfs_threaded(self):
        """Solve maze using BFS in a separate thread"""
        if not self.maze:
            messagebox.showwarning("Warning", "Please load a maze first!")
            return

        self.stop_animation()  # Stop any ongoing animation
        self.clear_solution()
        self.update_results("Solving with BFS...")

        def run_bfs():
            self.solver = MazeSolver(self.maze)
            found = self.solver.bfs()
            self.master.after(1, lambda: self._post_solve_bfs(found))

        threading.Thread(target=run_bfs, daemon=True).start()

    def _post_solve_bfs(self, found):
        if found:
            self.draw_solution("BFS", "blue")
            self.update_results(f"BFS Solution - Path Length: {self.solver.get_path_length()}, "
                                f"Steps Explored: {self.solver.steps_taken}, "
                                f"Time: {self.solver.solve_time:.4f}s")
        else:
            self.update_results("BFS: No solution found!")

    def compare_algorithms_threaded(self):
        """Compare DFS and BFS algorithms in a separate thread"""
        if not self.maze:
            messagebox.showwarning("Warning", "Please load a maze first!")
            return

        self.stop_animation()  # Stop any ongoing animation
        self.clear_solution()
        self.update_results("Comparing DFS and BFS...")

        def run_comparison():
            # Solve with DFS
            dfs_solver = MazeSolver(self.maze)
            dfs_found = dfs_solver.dfs()

            # Solve with BFS
            bfs_solver = MazeSolver(self.maze)
            bfs_found = bfs_solver.bfs()

            self.master.after(1, lambda: self._post_compare_algorithms(dfs_solver, bfs_solver, dfs_found, bfs_found))

        threading.Thread(target=run_comparison, daemon=True).start()

    def _post_compare_algorithms(self, dfs_solver, bfs_solver, dfs_found, bfs_found):
        # Display both solutions
        if dfs_found:
            self.draw_path(dfs_solver.path, "red", "DFS_comp")
        if bfs_found:
            self.draw_path(bfs_solver.path, "blue", "BFS_comp")

        # Update results
        results = "Algorithm Comparison:\n"
        if dfs_found:
            results += f"DFS - Length: {dfs_solver.get_path_length()}, Steps: {dfs_solver.steps_taken}, Time: {dfs_solver.solve_time:.4f}s\n"
        else:
            results += "DFS - No solution found\n"

        if bfs_found:
            results += f"BFS - Length: {bfs_solver.get_path_length()}, Steps: {bfs_solver.steps_taken}, Time: {bfs_solver.solve_time:.4f}s\n"
        else:
            results += "BFS - No solution found\n"

        if dfs_found and bfs_found:
            if dfs_solver.get_path_length() < bfs_solver.get_path_length():
                results += "DFS found shorter path!"
            elif bfs_solver.get_path_length() < dfs_solver.get_path_length():
                results += "BFS found shorter path!"
            else:
                results += "Both algorithms found paths of equal length!"

        self.update_results(results)

    def animate_dfs(self):
        """Animate DFS step by step"""
        if not self.maze:
            messagebox.showwarning("Warning", "Please load a maze first!")
            return

        self.stop_animation()  # Stop any ongoing animation
        self.clear_solution()
        self.update_results("Animating DFS...")
        self.solver = MazeSolver(self.maze)

        def run_animate_dfs():
            if self.solver.dfs(step_by_step=True):
                self.master.after(1, lambda: self.animate_solution("DFS", "red"))
            else:
                self.master.after(1, lambda: self.update_results("DFS: No solution found!"))

        threading.Thread(target=run_animate_dfs, daemon=True).start()

    def animate_bfs(self):
        """Animate BFS step by step"""
        if not self.maze:
            messagebox.showwarning("Warning", "Please load a maze first!")
            return

        self.stop_animation()  # Stop any ongoing animation
        self.clear_solution()
        self.update_results("Animating BFS...")
        self.solver = MazeSolver(self.maze)

        def run_animate_bfs():
            if self.solver.bfs(step_by_step=True):
                self.master.after(1, lambda: self.animate_solution("BFS", "blue"))
            else:
                self.master.after(1, lambda: self.update_results("BFS: No solution found!"))

        threading.Thread(target=run_animate_bfs, daemon=True).start()

    def animate_solution(self, algorithm, color):
        """Animate the step-by-step solution"""
        self.draw_maze()
        self.animation_stop_event.clear()  # Reset stop event for new animation

        def animate_step(step_index):
            if self.animation_stop_event.is_set():  # Check if stop event is set
                return

            if step_index >= len(self.solver.exploration_order):
                # Animation complete, draw final path
                self.draw_path(self.solver.path, color, algorithm)
                self.update_results(f"{algorithm} Animation Complete - "
                                    f"Path Length: {self.solver.get_path_length()}, "
                                    f"Steps Explored: {self.solver.steps_taken}")
                return

            action, cell = self.solver.exploration_order[step_index]
            row, col = cell

            # Convert canvas coordinates to cell coordinates for drawing
            x1_rect = col * self.cell_size + 2
            y1_rect = row * self.cell_size + 2
            x2_rect = x1_rect + self.cell_size - 4
            y2_rect = y1_rect + self.cell_size - 4

            # Avoid drawing over entrance/exit text, keep them visible
            if cell == self.maze.entrance or cell == self.maze.exit:
                fill_color = 'lightgreen' if cell == self.maze.entrance else 'pink'
            elif action == 'visit':
                fill_color = 'lightgray'
            elif action == 'explore':
                fill_color = 'lightyellow'
            else:
                fill_color = 'white'  # Default or unknown state

            self.canvas.create_rectangle(x1_rect, y1_rect, x2_rect, y2_rect, fill=fill_color, outline='gray',
                                         tags='animation')

            # Schedule next step
            self.master.after(self.speed_var.get(), lambda: animate_step(step_index + 1))

        animate_step(0)

    def toggle_edit_mode(self):
        """Toggle maze editing mode"""
        self.is_editing = self.edit_var.get()
        if self.is_editing:
            self.canvas.config(cursor="hand2")  # Change cursor to indicate editable area
            self.update_results("Edit Mode: ON. Click/drag to toggle walls, use radio buttons to set Entrance/Exit.")
        else:
            self.canvas.config(cursor="")
            self.update_results("Edit Mode: OFF.")

    def on_canvas_click(self, event):
        """Handle canvas click events for editing"""
        if not self.is_editing or not self.maze:
            return

        # Convert canvas coordinates to maze cell/wall coordinates
        # Adjust for scroll region offset if necessary, though canvasx/y should handle this.
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        col_at_click = int(canvas_x // self.cell_size)
        row_at_click = int(canvas_y // self.cell_size)

        mode = self.mode_var.get()

        if mode == "entrance":
            if 0 <= row_at_click < self.maze.rows and 0 <= col_at_click < self.maze.cols:
                self.maze.entrance = (row_at_click, col_at_click)
                self.draw_maze()
                self.update_results(f"Entrance set to: ({row_at_click},{col_at_click})")
            else:
                messagebox.showwarning("Warning", "Cannot set entrance outside maze boundaries.")
        elif mode == "exit":
            if 0 <= row_at_click < self.maze.rows and 0 <= col_at_click < self.maze.cols:
                self.maze.exit = (row_at_click, col_at_click)
                self.draw_maze()
                self.update_results(f"Exit set to: ({row_at_click},{col_at_click})")
            else:
                messagebox.showwarning("Warning", "Cannot set exit outside maze boundaries.")
        elif mode == "wall":
            self.handle_wall_editing(event)

    def on_canvas_drag(self, event):
        """Handle canvas drag events for wall editing"""
        if self.is_editing and self.mode_var.get() == "wall":
            self.handle_wall_editing(event)

    def handle_wall_editing(self, event):
        """Handle wall editing"""
        if not self.maze:
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Determine which cell and which part of the cell was clicked
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)

        x_in_cell = x % self.cell_size
        y_in_cell = y % self.cell_size

        wall_toggle_performed = False

        # Tolerance for clicking near a wall
        tolerance = 5

        # Horizontal walls (top and bottom of a cell)
        if y_in_cell < tolerance:  # Near top edge of cell (horizontal wall above current cell)
            if 0 <= row <= self.maze.rows and 0 <= col < self.maze.cols:
                self.maze.horizontal_walls[row][col] = not self.maze.horizontal_walls[row][col]
                wall_toggle_performed = True
        elif y_in_cell > self.cell_size - tolerance:  # Near bottom edge of cell (horizontal wall below current cell)
            if 0 <= row + 1 <= self.maze.rows and 0 <= col < self.maze.cols:
                self.maze.horizontal_walls[row + 1][col] = not self.maze.horizontal_walls[row + 1][col]
                wall_toggle_performed = True

        # Vertical walls (left and right of a cell)
        if x_in_cell < tolerance:  # Near left edge of cell (vertical wall to the left of current cell)
            if 0 <= row < self.maze.rows and 0 <= col <= self.maze.cols:
                self.maze.vertical_walls[row][col] = not self.maze.vertical_walls[row][col]
                wall_toggle_performed = True
        elif x_in_cell > self.cell_size - tolerance:  # Near right edge of cell (vertical wall to the right of current cell)
            if 0 <= row < self.maze.rows and 0 <= col + 1 <= self.maze.cols:
                self.maze.vertical_walls[row][col + 1] = not self.maze.vertical_walls[row][col + 1]
                wall_toggle_performed = True

        if wall_toggle_performed:
            self.draw_maze()  # Redraw maze to reflect changes
            self.clear_solution()  # Clear any existing solution when maze changes

    def clear_solution(self):
        """Clear the current solution display"""
        self.canvas.delete("solution")
        self.canvas.delete("animation")
        self.canvas.delete("DFS_comp")  # Clear comparison paths
        self.canvas.delete("BFS_comp")  # Clear comparison paths
        self.update_results("")  # Clear results text

    def draw_maze(self):
        """Draw the maze on canvas"""
        if not self.maze:
            return

        self.canvas.delete("all")

        # Draw cells
        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Draw cell background (e.g., light gray border)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='lightgray')

        # Draw walls
        # Horizontal walls
        for row in range(self.maze.rows + 1):
            for col in range(self.maze.cols):
                if self.maze.horizontal_walls[row][col]:
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1
                    self.canvas.create_line(x1, y1, x2, y2, width=3, fill='black', tags="wall")

        # Vertical walls
        for row in range(self.maze.rows):
            for col in range(self.maze.cols + 1):
                if self.maze.vertical_walls[row][col]:
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    x2 = x1
                    y2 = y1 + self.cell_size
                    self.canvas.create_line(x1, y1, x2, y2, width=3, fill='black', tags="wall")

        # Mark entrance and exit (draw these *after* walls to ensure they are on top)
        if self.maze.entrance:
            r, c = self.maze.entrance
            x_center = c * self.cell_size + self.cell_size // 2
            y_center = r * self.cell_size + self.cell_size // 2
            self.canvas.create_oval(x_center - 10, y_center - 10, x_center + 10, y_center + 10,
                                    fill='green', outline='darkgreen', tags="entrance_exit")
            self.canvas.create_text(x_center, y_center, text='A', font=('Arial', 10, 'bold'),
                                    fill='white', tags="entrance_exit_text")
        if self.maze.exit:
            r, c = self.maze.exit
            x_center = c * self.cell_size + self.cell_size // 2
            y_center = r * self.cell_size + self.cell_size // 2
            self.canvas.create_oval(x_center - 10, y_center - 10, x_center + 10, y_center + 10,
                                    fill='red', outline='darkred', tags="entrance_exit")
            self.canvas.create_text(x_center, y_center, text='B', font=('Arial', 10, 'bold'),
                                    fill='white', tags="entrance_exit_text")

        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, self.maze.cols * self.cell_size, self.maze.rows * self.cell_size))

    def draw_path(self, path, color, tag_suffix):
        """Draw a path on the canvas"""
        if not path:
            return

        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]

            x1_center = c1 * self.cell_size + self.cell_size // 2
            y1_center = r1 * self.cell_size + self.cell_size // 2
            x2_center = c2 * self.cell_size + self.cell_size // 2
            y2_center = r2 * self.cell_size + self.cell_size // 2

            self.canvas.create_line(x1_center, y1_center, x2_center, y2_center,
                                    fill=color, width=4, tags=("solution", tag_suffix))

    def draw_solution(self, algorithm, color):
        """Draw the solution path"""
        self.clear_solution()
        if self.solver and self.solver.path:
            self.draw_path(self.solver.path, color, algorithm)

    def update_results(self, text):
        """Update the results text display"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)


# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = MazeVisualizer(root)
    root.mainloop()