from libqtile.layout.base import Layout
from libqtile.command.base import expose_command
from libqtile.log_utils import logger

# --- These are the "nodes" of our layout tree ---
class _Node:
    def __init__(self):
        self.parent = None
        self.rect = (0, 0, 0, 0)
    
    def find_leaf_at(self, x, y):
        # Base method, overridden by children
        return None

class _SplitNode(_Node):
    def __init__(self, direction, child1, child2):
        _Node.__init__(self)
        self.direction = direction
        self.child1 = child1
        self.child2 = child2
        child1.parent = self
        child2.parent = self

    def find_leaf_at(self, x, y):
        # Recursively find the leaf at a given (x,y) coordinate
        sx, sy, sw, sh = self.rect
        if not (sx <= x < (sx + sw) and sy <= y < (sy + sh)):
            return None
        
        found = self.child1.find_leaf_at(x, y)
        if found:
            return found
            
        found = self.child2.find_leaf_at(x, y)
        if found:
            return found
            
        return None

class _LeafNode(_Node):
    def __init__(self, client, next_split_direction):
        _Node.__init__(self)
        self.client = client
        self.next_split_direction = next_split_direction

    def find_leaf_at(self, x, y):
        # Check if the (x,y) coordinate is within this leaf's rectangle
        lx, ly, lw, lh = self.rect
        if lx <= x < (lx + lw) and ly <= y < (ly + lh):
            return self
        return None

# --- This is the Layout class itself ---
class Dwindle(Layout):
    """
    Dwindle Layout
    
    Splits the focused window in an alternating "Right, Down, Right, Down..."
    pattern, with each split being 50/50.
    """
    defaults = [
        ("border_width", 2, "Border width"),
        ("margin", 4, "Margin"),
        ("border_focus", "#ff0000", "Border focus color"),
        ("border_normal", "#444444", "Border normal color"),
        ("ratio", 0.5, "Split ratio (0.5 = 50/50)"),
    ]

    def __init__(self, **config):
        Layout.__init__(self, **config)
        self.add_defaults(Dwindle.defaults)
        self.root_node = None
        self.leaves = {}  # Map client.wid to _LeafNode
        self.clients = [] # List of clients in add order for focus
    
    def clone(self, group):
        c = Layout.clone(self, group)
        c.root_node = None
        c.leaves = {}
        c.clients = []
        return c

    def add_client(self, client):
        # 1. Determine the next split direction
        if self.root_node is None:
            # This is the first window. The split *it* will create
            # when a new window is added will be "vertical".
            next_direction = "vertical"
        else:
            # Find the focused window to determine next split
            focused_client = self.group.current_window
            if focused_client and focused_client.wid in self.leaves:
                next_direction = self.leaves[focused_client.wid].next_split_direction
            else:
                # Fallback: just use the last window added
                last_client = self.clients[-1]
                next_direction = self.leaves[last_client.wid].next_split_direction

        # 2. Create the new leaf node for our new window
        # Its *own* next_split_direction will be the opposite.
        new_leaf = _LeafNode(
            client, 
            "horizontal" if next_direction == "vertical" else "vertical"
        )
        self.leaves[client.wid] = new_leaf
        self.clients.append(client)

        # 3. Insert the new leaf into the tree
        if self.root_node is None:
            # --- THIS IS THE FIX ---
            # The first leaf's `next_split_direction` must be "vertical"
            # so that the *first split* (when the 2nd window is added)
            # is vertical.
            new_leaf.next_split_direction = "vertical"
            # --- END FIX ---
            self.root_node = new_leaf
            return

        # Find the focused leaf and replace it with a new split
        focused_client = self.group.current_window
        if focused_client is None or focused_client.wid not in self.leaves:
            focused_client = self.clients[-2] # The one just before we added

        focused_leaf = self.leaves[focused_client.wid]
        parent = focused_leaf.parent
        
        # New split node contains the old leaf (child1) and new leaf (child2)
        new_split = _SplitNode(next_direction, focused_leaf, new_leaf)
        
        # Update the old leaf's split direction to match the new leaf's
        focused_leaf.next_split_direction = new_leaf.next_split_direction

        # 4. Link the new split node into the tree
        if parent is None:
            self.root_node = new_split
        else:
            if parent.child1 == focused_leaf:
                parent.child1 = new_split
            else:
                parent.child2 = new_split
            new_split.parent = parent
            
    def remove(self, client):
        if client.wid not in self.leaves:
            return

        self.clients.remove(client)
        leaf = self.leaves.pop(client.wid)
        
        if self.root_node == leaf:
            self.root_node = None
            return

        parent_split = leaf.parent
        sibling = parent_split.child1 if parent_split.child2 == leaf else parent_split.child2
        grandparent = parent_split.parent

        if grandparent is None:
            self.root_node = sibling
            sibling.parent = None
            
            # --- THIS IS THE FIX ---
            # If the new root is a leaf (i.e., it's the only window left),
            # we must reset its next_split_direction to "vertical"
            # so the *next* window added will split vertically.
            if isinstance(self.root_node, _LeafNode):
                self.root_node.next_split_direction = "vertical"
            # --- END FIX ---
                
        else:
            if grandparent.child1 == parent_split:
                grandparent.child1 = sibling
            else:
                grandparent.child2 = sibling
            sibling.parent = grandparent
        
    def _calculate_rects(self, node, rect):
        node.rect = rect
        if isinstance(node, _SplitNode):
            x, y, w, h = rect
            r = self.ratio
            
            if node.direction == "vertical":
                # [Old Window | New Window]
                rect1 = (x, y, int(w * r), h)
                rect2 = (x + int(w * r), y, int(w * (1 - r)), h)
            else: # "horizontal"
                # [Old Window]
                # [New Window]
                rect1 = (x, y, w, int(h * r))
                rect2 = (x, y + int(h * r), w, int(h * (1 - r)))
            
            self._calculate_rects(node.child1, rect1)
            self._calculate_rects(node.child2, rect2)

    def configure(self, client, screen_rect):
        if not self.root_node or client.wid not in self.leaves:
            client.hide()
            return
            
        # Recalculate all rectangles on every configure
        self._calculate_rects(self.root_node, (
            screen_rect.x,
            screen_rect.y,
            screen_rect.width,
            screen_rect.height
        ))
        
        node = self.leaves[client.wid]
        x, y, w, h = node.rect

        # Calculate final dimensions *before* placing
        calculated_width = w - (self.border_width * 2)
        calculated_height = h - (self.border_width * 2)

        # Check if dimensions are valid (greater than 0)
        if calculated_width <= 0 or calculated_height <= 0:
             # If not, hide the window instead of trying to place it
             logger.warning(f"Dwindle: Hiding client {client.name} due to invalid size ({calculated_width}x{calculated_height}).")
             client.hide()
             return # Stop processing this client

        client.place(
            x,
            y,
            w - (self.border_width * 2),
            h - (self.border_width * 2),
            self.border_width,
            self.border_focus if client.has_focus else self.border_normal,
            margin=self.margin,
        )
        client.unhide()

    def info(self):
        return {"clients": [c.name for c in self.clients]}

    # --- Client/Focus Access ---
    
    @property
    def current_client(self):
        return self.group.current_window

    def focus_first(self):
        if self.clients:
            return self.clients[0]

    def focus_last(self):
        if self.clients:
            return self.clients[-1]

    def focus_next(self, client):
        if client not in self.clients:
            return
        idx = self.clients.index(client)
        if idx + 1 < len(self.clients):
            return self.clients[idx + 1]
        
    def focus_previous(self, client):
        if client not in self.clients:
            return
        idx = self.clients.index(client)
        if idx > 0:
            return self.clients[idx - 1]

    # --- "Next" / "Previous" Navigation (Mod+Space) ---

    @expose_command()
    def next(self):
        client = self.focus_next(self.current_client)
        self.group.focus(client, True)

    @expose_command()
    def previous(self):
        client = self.focus_previous(self.current_client)
        self.group.focus(client, True)
    
    # --- HJKL Directional Navigation ---

    def _find_neighbor(self, direction):
        current_client = self.group.current_window
        if not current_client or current_client.wid not in self.leaves:
            return None
            
        leaf = self.leaves[current_client.wid]
        x, y, w, h = leaf.rect
        
        # Find a coordinate just outside the current window
        # in the direction we want to move
        target_x, target_y = x, y
        
        if direction == "left":
            target_x = x - 1
            target_y = y + h // 2
        elif direction == "right":
            target_x = x + w + 1
            target_y = y + h // 2
        elif direction == "up":
            target_x = x + w // 2
            target_y = y - 1
        elif direction == "down":
            target_x = x + w // 2
            target_y = y + h + 1
            
        if not self.root_node:
            return None
        
        # Find whatever leaf exists at that target coordinate
        neighbor_leaf = self.root_node.find_leaf_at(target_x, target_y)
        
        if neighbor_leaf:
            return neighbor_leaf.client
        return None

    @expose_command()
    def up(self):
        """Focus window above current"""
        neighbor = self._find_neighbor("up")
        if neighbor:
            self.group.focus(neighbor, True)

    @expose_command()
    def down(self):
        """Focus window below current"""
        neighbor = self._find_neighbor("down")
        if neighbor:
            self.group.focus(neighbor, True)
        
    @expose_command()
    def left(self):
        """Focus window to the left of current"""
        neighbor = self._find_neighbor("left")
        if neighbor:
            self.group.focus(neighbor, True)

    @expose_command()
    def right(self):
        """Focus window to the right of current"""
        neighbor = self._find_neighbor("right")
        if neighbor:
            self.group.focus(neighbor, True)

    # --- HJKL Directional Shuffling (Swapping) ---
    
    def _swap_clients(self, client1, client2):
        """Swaps two clients in the layout tree"""
        if not client1 or not client2 or client1.wid not in self.leaves or client2.wid not in self.leaves:
            return

        node1 = self.leaves[client1.wid]
        node2 = self.leaves[client2.wid]
        
        parent1 = node1.parent
        parent2 = node2.parent

        if not parent1 or not parent2:
            # Should not happen unless one is the root, which we can't swap
            logger.warning("Dwindle layout: Cannot swap nodes.")
            return

        # Swap nodes in the tree structure
        if parent1 == parent2:
            # They are siblings, just swap them
            if parent1.child1 == node1:
                parent1.child1 = node2
                parent1.child2 = node1
            else:
                parent1.child1 = node1
                parent1.child2 = node2
        else:
            # They have different parents, swap their parent's references
            if parent1.child1 == node1:
                parent1.child1 = node2
            else:
                parent1.child2 = node2
            
            if parent2.child1 == node2:
                parent2.child1 = node1
            else:
                parent2.child2 = node1
            
            # Finally, swap their own parent pointers
            node1.parent, node2.parent = parent2, parent1
        
        # Swap them in the focus list as well
        try:
            idx1 = self.clients.index(client1)
            idx2 = self.clients.index(client2)
            self.clients[idx1], self.clients[idx2] = self.clients[idx2], self.clients[idx1]
        except ValueError:
            pass # Should not happen

        # Force a redraw
        self.group.layout_all(autoswap=True)

    @expose_command()
    def shuffle_left(self):
        """Swap focused window with window to the left"""
        neighbor = self._find_neighbor("left")
        if neighbor:
            self._swap_clients(self.current_client, neighbor)

    @expose_command()
    def shuffle_right(self):
        """Swap focused window with window to the right"""
        neighbor = self._find_neighbor("right")
        if neighbor:
            self._swap_clients(self.current_client, neighbor)

    @expose_command()
    def shuffle_up(self):
        """Swap focused window with window above"""
        neighbor = self._find_neighbor("up")
        if neighbor:
            self._swap_clients(self.current_client, neighbor)

    @expose_command()
    def shuffle_down(self):
        """Swap focused window with window below"""
        neighbor = self._find_neighbor("down")
        if neighbor:
            self._swap_clients(self.current_client, neighbor)
