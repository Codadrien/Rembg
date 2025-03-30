from rembg import remove
from PIL import Image
import os
import numpy as np

def remove_background_and_resize(input_path, output_path):
    try:
        print(f"Tentative d'ouverture de l'image : {input_path}")
        print(f"Chemin absolu : {os.path.abspath(input_path)}")
        
        # Ouvrir l'image
        input_image = Image.open(input_path)
        
        print("Image ouverte avec succès")
        print(f"Format de l'image : {input_image.format}")
        print(f"Mode de l'image : {input_image.mode}")
        print(f"Taille de l'image : {input_image.size}")
        
        # Supprimer le fond avec des paramètres optimisés pour les ombres
        output_image = remove(input_image)
        
        # Convertir en numpy array pour le traitement
        img_array = np.array(output_image)
        
        # Créer un masque pour les pixels non-transparents avec un seuil minimal
        alpha_mask = img_array[:, :, 3] > 1  # Seuil minimal pour garder les ombres
        
        # Trouver les limites de l'image non-transparente
        rows = np.any(alpha_mask, axis=1)
        cols = np.any(alpha_mask, axis=0)
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        
        # Recadrer l'image pour enlever les bords vides (sans marge)
        cropped_image = output_image.crop((xmin, ymin, xmax + 1, ymax + 1))
        
        # Créer un fond blanc
        width, height = cropped_image.size
        max_size = max(width, height)
        square_size = max_size
        
        # Créer une nouvelle image carrée blanche
        square_image = Image.new('RGBA', (square_size, square_size), (255, 255, 255, 255))
        
        # Calculer la position pour centrer l'image
        x = (square_size - width) // 2
        y = (square_size - height) // 2
        
        # Coller l'image sans fond sur le fond blanc
        square_image.paste(cropped_image, (x, y), cropped_image)
        
        # Sauvegarder l'image
        square_image.save(output_path)
        print(f"Image sauvegardée dans : {output_path}")
        print(f"Nouvelle taille : {square_size}x{square_size}")
        
    except Exception as e:
        print(f"Erreur lors du traitement de l'image : {str(e)}")
        print(f"Le fichier existe ? {os.path.exists(input_path)}")
        if os.path.exists(input_path):
            print(f"Taille du fichier : {os.path.getsize(input_path)} bytes")

if __name__ == "__main__":
    # Créer un dossier pour les images si nécessaire
    if not os.path.exists("images"):
        os.makedirs("images")
    
    # Exemple d'utilisation
    input_path = "images/input.jpg"  # Remplacez par le chemin de votre image
    output_path = "images/output.png"
    
    remove_background_and_resize(input_path, output_path) 