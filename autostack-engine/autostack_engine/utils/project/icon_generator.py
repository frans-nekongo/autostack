from PIL import Image
import hashlib
import io
import base64


class IdenticonGenerator:
    """Generate GitHub-style identicons using py-identicon algorithm"""
    
    @staticmethod
    def generate_identicon(text: str, size: int = 200) -> tuple[Image.Image, str]:
        """
        Generate a 5x5 GitHub-style identicon
        
        Args:
            text: Input string (username, email, etc.)
            size: Output image size in pixels
            
        Returns:
            tuple of (PIL Image, hash string)
        """
        # Create hash from input
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to color (RGB)
        color = tuple(int(hash_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Create 5x5 grid (only need 3 columns due to symmetry)
        grid = [[0 for _ in range(3)] for _ in range(5)]
        
        # Use hash to determine which pixels are filled
        for i in range(5):
            for j in range(3):
                idx = i * 3 + j
                if idx < len(hash_hex):
                    grid[i][j] = int(hash_hex[idx], 16) % 2
        
        # Create image
        pixel_size = size // 5
        img = Image.new('RGB', (size, size), 'white')
        pixels = img.load()
        
        # Draw the identicon with symmetry
        for i in range(5):
            for j in range(5):
                grid_col = j if j < 3 else 4 - j
                if grid[i][grid_col] == 1:
                    for x in range(j * pixel_size, (j + 1) * pixel_size):
                        for y in range(i * pixel_size, (i + 1) * pixel_size):
                            if x < size and y < size:
                                pixels[x, y] = color
        
        return img, hash_hex
    
    @staticmethod
    def image_to_base64(img: Image.Image, format: str = 'PNG') -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    @staticmethod
    def base64_to_data_url(base64_str: str, format: str = 'png') -> str:
        """Convert base64 to data URL for direct HTML rendering"""
        return f"data:image/{format};base64,{base64_str}"
