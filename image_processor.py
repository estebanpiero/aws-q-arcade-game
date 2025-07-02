"""
Image Processor for AWS Breakout Game
Converts AWS service logo images into 2D brick grids using PIL
"""

from PIL import Image, ImageEnhance
import json
import os
import numpy as np
from typing import List, Dict, Tuple, Optional

class ImageProcessor:
    """Converts AWS service logo images into brick grid layouts for the game"""
    
    def __init__(self, grid_width: int = 20, grid_height: int = 15):
        """
        Initialize the image processor
        
        Args:
            grid_width: Number of brick columns in the game grid
            grid_height: Number of brick rows in the game grid
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Color mapping for different brick types based on image colors
        self.color_map = {
            'orange': (255, 153, 0),    # EC2 orange
            'green': (35, 47, 62),      # S3 green/dark
            'blue': (35, 47, 62),       # General AWS blue
            'purple': (146, 43, 140),   # Lambda purple
            'red': (214, 51, 132),      # Error/warning red
            'yellow': (255, 204, 0),    # Warning yellow
            'light_blue': (135, 206, 235), # Light blue
            'dark_blue': (25, 25, 112),    # Dark blue
        }
    
    def load_and_preprocess_image(self, image_path: str, target_size: Optional[Tuple[int, int]] = None) -> Image.Image:
        """
        Load and preprocess an AWS service logo image
        
        Args:
            image_path: Path to the image file
            target_size: Optional target size (width, height) for resizing
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Load the image
            img = Image.open(image_path)
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize if target size is specified
            if target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            else:
                # Default resize to fit our grid proportions
                aspect_ratio = img.width / img.height
                if aspect_ratio > (self.grid_width / self.grid_height):
                    # Image is wider, fit to width
                    new_width = self.grid_width * 20  # 20 pixels per grid cell
                    new_height = int(new_width / aspect_ratio)
                else:
                    # Image is taller, fit to height
                    new_height = self.grid_height * 20
                    new_width = int(new_height * aspect_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Enhance contrast to make logo features more distinct
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            return img
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def image_to_grid(self, image_path: str, service_name: str, threshold: int = 128) -> Dict:
        """
        Convert an AWS service logo image to a brick grid layout
        
        Args:
            image_path: Path to the AWS service logo image
            service_name: Name of the AWS service (e.g., "EC2", "S3")
            threshold: Alpha threshold for determining if a pixel should be a brick
            
        Returns:
            Dictionary containing the brick layout data
        """
        img = self.load_and_preprocess_image(image_path)
        if img is None:
            return None
        
        # Convert image to numpy array for easier processing
        img_array = np.array(img)
        
        # Calculate grid cell size
        cell_width = img.width // self.grid_width
        cell_height = img.height // self.grid_height
        
        bricks = []
        
        # Process each grid cell
        for grid_y in range(self.grid_height):
            for grid_x in range(self.grid_width):
                # Calculate pixel boundaries for this grid cell
                start_x = grid_x * cell_width
                end_x = min(start_x + cell_width, img.width)
                start_y = grid_y * cell_height
                end_y = min(start_y + cell_height, img.height)
                
                # Extract the cell region
                cell_region = img_array[start_y:end_y, start_x:end_x]
                
                # Check if this cell should contain a brick
                if self._should_place_brick(cell_region, threshold):
                    # Determine brick color based on the dominant color in the cell
                    brick_color = self._get_dominant_color(cell_region)
                    
                    # Add brick to the layout
                    bricks.append({
                        "x": grid_x,
                        "y": grid_y,
                        "color": brick_color,
                        "durability": 1
                    })
        
        # Create the level data structure
        level_data = {
            "name": service_name,
            "description": f"AWS {service_name} Service Logo",
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "bricks": bricks,
            "source_image": os.path.basename(image_path)
        }
        
        return level_data
    
    def _should_place_brick(self, cell_region: np.ndarray, threshold: int) -> bool:
        """
        Determine if a grid cell should contain a brick based on pixel data
        
        Args:
            cell_region: Numpy array of the cell's pixel data
            threshold: Alpha threshold for brick placement
            
        Returns:
            True if a brick should be placed in this cell
        """
        if cell_region.size == 0:
            return False
        
        # Check alpha channel (transparency)
        alpha_channel = cell_region[:, :, 3]
        
        # Calculate the percentage of non-transparent pixels
        non_transparent_pixels = np.sum(alpha_channel > threshold)
        total_pixels = alpha_channel.size
        
        # Place a brick if more than 30% of pixels are non-transparent
        return (non_transparent_pixels / total_pixels) > 0.3
    
    def _get_dominant_color(self, cell_region: np.ndarray) -> str:
        """
        Get the dominant color name for a cell region
        
        Args:
            cell_region: Numpy array of the cell's pixel data
            
        Returns:
            Color name string
        """
        if cell_region.size == 0:
            return 'blue'
        
        # Get non-transparent pixels
        alpha_mask = cell_region[:, :, 3] > 128
        if not np.any(alpha_mask):
            return 'blue'
        
        # Calculate average RGB values for non-transparent pixels
        rgb_pixels = cell_region[alpha_mask][:, :3]
        avg_color = np.mean(rgb_pixels, axis=0)
        
        # Find the closest color in our color map
        min_distance = float('inf')
        closest_color = 'blue'
        
        for color_name, color_rgb in self.color_map.items():
            distance = np.sqrt(np.sum((avg_color - np.array(color_rgb)) ** 2))
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        return closest_color
    
    def process_all_images(self, images_dir: str, output_dir: str) -> List[str]:
        """
        Process all AWS service images in a directory and generate level files
        
        Args:
            images_dir: Directory containing AWS service logo images
            output_dir: Directory to save the generated level JSON files
            
        Returns:
            List of generated level file paths
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        generated_files = []
        
        # Supported image formats
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(supported_formats):
                image_path = os.path.join(images_dir, filename)
                
                # Extract service name from filename (remove extension)
                service_name = os.path.splitext(filename)[0].upper()
                
                print(f"Processing {service_name} logo...")
                
                # Convert image to grid
                level_data = self.image_to_grid(image_path, service_name)
                
                if level_data and level_data['bricks']:
                    # Save level data to JSON file
                    output_filename = f"{service_name.lower()}_logo.json"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, 'w') as f:
                        json.dump(level_data, f, indent=2)
                    
                    generated_files.append(output_path)
                    print(f"Generated level file: {output_filename} ({len(level_data['bricks'])} bricks)")
                else:
                    print(f"Warning: No bricks generated for {service_name}")
        
        return generated_files
    
    def preview_grid(self, level_data: Dict) -> str:
        """
        Generate a text preview of the brick grid layout
        
        Args:
            level_data: Level data dictionary
            
        Returns:
            String representation of the grid
        """
        grid = [['.' for _ in range(level_data['grid_width'])] for _ in range(level_data['grid_height'])]
        
        # Color symbols for preview
        color_symbols = {
            'orange': 'O',
            'green': 'G',
            'blue': 'B',
            'purple': 'P',
            'red': 'R',
            'yellow': 'Y',
            'light_blue': 'L',
            'dark_blue': 'D'
        }
        
        # Place bricks in the grid
        for brick in level_data['bricks']:
            symbol = color_symbols.get(brick['color'], 'X')
            grid[brick['y']][brick['x']] = symbol
        
        # Convert grid to string
        preview = f"\n{level_data['name']} Logo Preview:\n"
        preview += "=" * (level_data['grid_width'] + 2) + "\n"
        
        for row in grid:
            preview += "|" + "".join(row) + "|\n"
        
        preview += "=" * (level_data['grid_width'] + 2) + "\n"
        preview += f"Total bricks: {len(level_data['bricks'])}\n"
        
        return preview

def main():
    """Example usage of the ImageProcessor"""
    processor = ImageProcessor(grid_width=20, grid_height=15)
    
    # Process all images in the images directory
    images_dir = "images"
    levels_dir = "assets/levels"
    
    if os.path.exists(images_dir):
        generated_files = processor.process_all_images(images_dir, levels_dir)
        print(f"\nGenerated {len(generated_files)} level files:")
        for file_path in generated_files:
            print(f"  - {file_path}")
    else:
        print(f"Images directory '{images_dir}' not found.")
        print("Please add AWS service logo images to the 'images' directory and run this script again.")

if __name__ == "__main__":
    main()
