import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from rembg import remove
import os
import threading
import tempfile

# Tentative d'import du plugin AVIF
try:
    from pillow_avif_plugin import register_avif_opener
    register_avif_opener()
    AVIF_SUPPORT = True
except ImportError:
    AVIF_SUPPORT = False
    print("Support AVIF non disponible. Les fichiers AVIF ne seront pas supportés.")

class BackgroundRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Remove Background Tool")
        
        # Variables
        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.processing = False
        
        # Interface
        self.create_widgets()
        
        # Configurer le redimensionnement de la fenêtre
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Lier le redimensionnement de la fenêtre
        self.root.bind('<Configure>', self.on_window_resize)
        
    def create_widgets(self):
        # Boutons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(button_frame, text="Choisir une image", command=self.load_image).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sauvegarder", command=self.save_image).pack(side="left", padx=5)
        
        # Frame pour l'image
        image_frame = ttk.Frame(self.root)
        image_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Canvas pour l'image
        self.canvas = tk.Canvas(image_frame, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        # Label pour le statut
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.grid(row=2, column=0, padx=5, pady=5)
        
    def resize_image(self, image, max_size=None):
        if max_size is None:
            # Obtenir la taille du canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculer le ratio pour redimensionner l'image
            ratio = min(canvas_width/image.width, canvas_height/image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
        else:
            # Calculer le ratio pour redimensionner l'image
            ratio = min(max_size/image.width, max_size/image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            
        return image.resize(new_size, Image.Resampling.LANCZOS)
        
    def convert_to_png(self, image_path):
        """Convertit une image en PNG et retourne le chemin du fichier temporaire"""
        try:
            print(f"Tentative de conversion de : {image_path}")
            # Créer un fichier temporaire
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(image_path)}.png")
            print(f"Fichier temporaire créé : {temp_file}")
            
            # Ouvrir l'image
            print("Ouverture de l'image...")
            img = Image.open(image_path)
            print(f"Format de l'image : {img.format}")
            print(f"Mode de l'image : {img.mode}")
            
            # Convertir en RGBA si nécessaire
            if img.mode != 'RGBA':
                print("Conversion en mode RGBA...")
                img = img.convert('RGBA')
            
            # Sauvegarder en PNG
            print("Sauvegarde en PNG...")
            img.save(temp_file, 'PNG')
            print("Conversion terminée avec succès")
            return temp_file
        except Exception as e:
            print(f"Erreur détaillée : {str(e)}")
            raise Exception(f"Erreur lors de la conversion en PNG : {str(e)}")
        
    def load_image(self):
        # Définir les types de fichiers acceptés
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
        if AVIF_SUPPORT:
            filetypes[0] = ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.avif")
            
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            try:
                self.status_label.config(text="Conversion de l'image en cours...")
                print(f"Tentative d'ouverture de : {file_path}")
                
                # Vérifier si c'est un format AVIF et si le support est disponible
                if file_path.lower().endswith('.avif') and not AVIF_SUPPORT:
                    messagebox.showerror("Erreur", "Le support AVIF n'est pas disponible. Veuillez convertir votre image en PNG ou WebP avant de l'utiliser.")
                    return
                
                # Convertir en PNG si c'est un WebP ou AVIF
                if file_path.lower().endswith(('.webp', '.avif')):
                    print(f"Format détecté : {file_path.split('.')[-1].upper()}")
                    temp_file = self.convert_to_png(file_path)
                    print("Ouverture de l'image convertie...")
                    self.original_image = Image.open(temp_file)
                    # Supprimer le fichier temporaire après utilisation
                    try:
                        os.remove(temp_file)
                        print("Fichier temporaire supprimé")
                    except Exception as e:
                        print(f"Erreur lors de la suppression du fichier temporaire : {str(e)}")
                else:
                    print("Format standard, ouverture directe...")
                    self.original_image = Image.open(file_path)
                
                self.process_image()
            except Exception as e:
                error_msg = f"Erreur lors de l'ouverture de l'image : {str(e)}"
                print(error_msg)
                self.status_label.config(text=error_msg)
    
    def process_image(self):
        if self.original_image is None:
            return
            
        try:
            self.status_label.config(text="Traitement en cours...")
            
            # Supprimer le fond avec rembg avec les paramètres optimaux
            output_image = remove(
                self.original_image,
                alpha_matting=True,
                alpha_matting_foreground_threshold=180,  # Plus bas pour plus de détails
                alpha_matting_background_threshold=100,  # Plus haut pour plus d'ombre
                alpha_matting_erode_size=5              # Plus petit pour des bords plus fins
            )
            
            # Convertir en numpy array pour le traitement
            img_array = np.array(output_image)
            
            # Trouver les coordonnées non transparentes
            alpha_channel = img_array[:, :, 3]
            rows = np.any(alpha_channel > 0, axis=1)
            cols = np.any(alpha_channel > 0, axis=0)
            
            # Trouver les limites de l'objet
            ymin, ymax = np.where(rows)[0][[0, -1]]
            xmin, xmax = np.where(cols)[0][[0, -1]]
            
            # Calculer la taille du carré
            size = max(ymax - ymin, xmax - xmin)
            
            # Créer une nouvelle image blanche carrée
            new_size = size + 20  # Ajouter une petite marge
            new_image = Image.new('RGBA', (new_size, new_size), (255, 255, 255, 255))
            
            # Calculer la position pour centrer l'objet
            x_offset = (new_size - (xmax - xmin)) // 2
            y_offset = (new_size - (ymax - ymin)) // 2
            
            # Coller l'objet centré
            new_image.paste(output_image.crop((xmin, ymin, xmax, ymax)), 
                          (x_offset, y_offset), 
                          output_image.crop((xmin, ymin, xmax, ymax)))
            
            # Sauvegarder l'image traitée
            self.processed_image = new_image
            
            # Mettre à jour l'affichage
            self.update_display()
            
            self.status_label.config(text="Traitement terminé")
            
        except Exception as e:
            self.status_label.config(text=f"Erreur : {str(e)}")
    
    def update_display(self):
        if self.processed_image is not None:
            # Redimensionner l'image pour l'affichage
            display_image = self.resize_image(self.processed_image)
            self.display_image = ImageTk.PhotoImage(display_image)
            
            # Mettre à jour le canvas
            self.canvas.delete("all")
            
            # Centrer l'image dans le canvas
            x = (self.canvas.winfo_width() - display_image.width) // 2
            y = (self.canvas.winfo_height() - display_image.height) // 2
            self.canvas.create_image(x, y, anchor="nw", image=self.display_image)
    
    def save_image(self):
        if self.processed_image is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("WebP files", "*.webp")]
        )
        if file_path:
            try:
                if file_path.lower().endswith('.webp'):
                    # Pour WebP, on doit spécifier la qualité
                    self.processed_image.save(file_path, 'WEBP', quality=90)
                else:
                    self.processed_image.save(file_path)
                self.status_label.config(text="Image sauvegardée")
            except Exception as e:
                self.status_label.config(text=f"Erreur lors de la sauvegarde : {str(e)}")

    def on_window_resize(self, event):
        if self.original_image is not None:
            self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Taille initiale de la fenêtre
    app = BackgroundRemoverGUI(root)
    root.mainloop() 