import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
import os
import socket
import threading
import json

class HomePlanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Planificador de Planos de Casa")
        self.root.state("zoomed")
        self._create_menu()
        self.canvas = tk.Canvas(self.root, bg="white", width=1920, height=1080)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.sensores_1piso = {
            "Distancia": {"x": 850, "y": 600, "valor": 0.0, "color": "green"},
            "Luz": {"x": 575, "y": 530, "valor": 0.0, "color": "blue"},
            
        }
        self.sensores_2piso = {
            "Humedad": {"x": 740, "y": 330, "valor": 0.0, "color": "green"},
            "Temperatura": {"x": 640, "y": 330, "valor": 0.0 , "color": "green"},
        }
        self.sensores = self.sensores_1piso
        self.ref_images = self._load_images()
        self.show_2d()
        threading.Thread(target=self.recibir_datos, daemon=True).start()

    def _load_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, "images")
        try:
            return [
                ImageTk.PhotoImage(
                    Image.open(os.path.join(images_dir, f"ref{i+1}.png")).resize((550, 500))
                ) for i in range(2)
            ]
        except:
            return []

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Vista 2D PRIMER PISO", command=self.show_2d)
        view_menu.add_command(label="Vista 2D SEGUNDO PISO", command=self.show_2d2st)
        view_menu.add_command(label="Vista 3D", command=self.show_3d)
        view_menu.add_command(label="Referencias", command=self.show_references)
        menubar.add_cascade(label="Vista", menu=view_menu)
        self.root.config(menu=menubar)

    def clear(self):
        self.canvas.delete("all")

    def insertar_imagen_canvas(self, imagen_relativa, x, y, ancho=50, alto=50, rotar=False):
        """
        Inserta una imagen en el canvas de Tkinter en la posición (x, y).
        imagen_relativa: ruta relativa a la carpeta del proyecto, por ejemplo 'images/sofa1.png'
        """
        # Obtiene la ruta absoluta del directorio donde está este archivo .py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        imagen_path = os.path.join(base_dir, imagen_relativa)
        img = Image.open(imagen_path)
        if rotar:
            img = img.rotate(90, expand=True)
        img = img.resize((ancho, alto), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(x, y, image=img_tk, anchor=tk.NW)
        if not hasattr(self, 'imagenes_tk'):
            self.imagenes_tk = []
        self.imagenes_tk.append(img_tk)

    def show_2d(self):
        self.clear()
        th_wall = 4
        self.sensores = self.sensores_1piso
        ##SENSORES
        #sensor_luz = self.canvas.create_oval(540, 540, 600, 600, fill="blue", outline="black" )
        #canvas_text = self.canvas.create_text(570, 530, text="Sensor Luz", font=(None, 10), fill="black")

        #######
        # Pared exterior (rectángulo con esquina diagonal)
        corners = [
            (400, 50),    # superior izquierda
            (900, 50),   # superior derecha
            (900, 580),  # punto medio en lado derecho
            (840, 650),   # vértice diagonal inferior derecho
            (400, 650)    # inferior izquierda
        ]

        for i in range(len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % len(corners)]
            self.canvas.create_line(x1, y1, x2, y2, width=th_wall)
        # División interna: solo línea horizontal un poco más arriba de la mitad
        # Línea horizontal (por ejemplo, a 250 en Y)
        self.canvas.create_line(400, 275, 650, 275, width=th_wall)
        self.canvas.create_line(725, 275, 900, 275, width=th_wall)
        # Linea chica vertical al final de la linea de arriba
        self.canvas.create_line(650, 275, 650, 265, width=th_wall)
        #Linea vertical en 650, 50 en y, pareeeeeed --- hacia abajo
        self.canvas.create_line(650, 50, 650, 125, width=th_wall)
        # Linea hacia la derecha desde el final de la linea vertical
        self.canvas.create_line(650, 125, 700, 125, width=th_wall)
        # Linea vertical hacia abajo desde el final de la linea horizontal
        self.canvas.create_line(700, 125, 700, 200, width=th_wall)
        # Linea horizontal hacia la izquierda desde el final de la linea vertical
        self.canvas.create_line(705, 200, 650, 200, width=th_wall)
        # Linea chica vertical hacia abajo desde el final de la linea horizontal
        self.canvas.create_line(650, 195, 650, 210, width=th_wall)

        # decoracion del cuarto de la izquierda
        #cama 
        self.canvas.create_rectangle(410, 120, 550, 200, outline="black", width=1, fill="lightyellow")
        self.canvas.create_rectangle(410, 60, 440, 110, outline="black", width=1, fill="#F1D191")
        self.canvas.create_text(450, 160, text="Cama", font=(None, 10), fill="black")
        self.canvas.create_rectangle(410, 210 , 440, 260, outline="black", width=1, fill="#F1D191")

        self.canvas.create_rectangle(530, 60, 640, 90, outline="black", width=1, fill="#F1D191")

        ######### Cuarto de la mitad #########
        # Linea vertical hacia abajo a 750, 50 en y, hasta 750 120 en y
        self.canvas.create_line(815, 50, 815, 110, width=th_wall)
        # Linea horizontal a la izquierda desde el final de la linea vertical
        self.canvas.create_line(815, 110, 770, 110, width=th_wall)
        
        # Linea vertical hacia abajo desde casi la mitad de la linea horizontal
        self.canvas.create_line(792, 110, 792, 210, width=th_wall)
        # Linea horizontal hacia la izquierda
        self.canvas.create_line(815, 200, 750, 200, width=th_wall)
        self.canvas.create_rectangle(705, 199, 710, 160, outline="black", width=1, fill="")

        # T debajo de ese cuarto
        self.canvas.create_line(792, 275, 792, 265, width=th_wall)
        #banoo
        self.canvas.create_line(770, 50, 770, 200, width=1)

        ####### Tercero de la derecha ########
        # Linea horizontal a la izquierda desde y = 110
        self.canvas.create_line(900, 110, 880, 110, width=th_wall)
        # linea vertical 50 antes del final del cuadrado
        self.canvas.create_line(880, 50, 880, 110, width=1)

        #Cocina

        self.canvas.create_line(725, 275, 725, 335, width=1)
        # 6 lineas con 1 de espacio desde 275 a 295
        self.canvas.create_line(725, 296, 880, 296, width=1)
        self.canvas.create_line(725, 280, 880, 280, width=1)
        self.canvas.create_line(725, 285, 880, 285, width=1)
        self.canvas.create_line(725, 290, 880, 290, width=1)
        self.canvas.create_line(725, 295, 880, 295, width=1)
        self.canvas.create_line(790, 295, 790, 335, width=1)
        self.canvas.create_line(725, 335, 840, 335, width=1)
        self.canvas.create_line(840, 335, 840, 530, width=1)

        # Rectángulo 1
        self.canvas.create_rectangle(440, 45, 480, 55, outline="gray", width=1, fill="lightgray")
        y_center1 = (45 + 55) / 2
        self.canvas.create_line(440, y_center1, 480, y_center1, dash=(3, 5), fill="black")

        self.canvas.create_rectangle(440 , 650, 540, 660, outline="gray", width=1, fill="lightgray")
        self.canvas.create_rectangle(680 , 645, 780, 655, outline="gray", fill="lightgray", width=1)

        # Rectángulo 2
        self.canvas.create_rectangle(700, 45, 740, 55, outline="gray", width=1, fill="lightgray")
        y_center2 = (45 + 55) / 2
        self.canvas.create_line(700, y_center2, 740, y_center2, dash=(3, 5), fill="black")

        # Rectángulo 3
        self.canvas.create_rectangle(820, 45, 860, 55, outline="gray", width=1, fill="lightgray")
        y_center3 = (45 + 55) / 2
        self.canvas.create_line(820, y_center3, 860, y_center3, dash=(3, 5), fill="black")

        self.canvas.create_rectangle(895, 270, 905, 210, outline="gray", width=1, fill="white")
        self.canvas.create_rectangle(840, 265, 895, 269, outline="black", width=1, fill="")
        self.canvas.create_rectangle(740, 265, 792, 269, outline="black", width=1, fill="")
        self.canvas.create_rectangle(600, 265, 650, 269, outline="black", width=1, fill="")
####### ESCALERAAAAAAAAAAAAS
        self.canvas.create_rectangle(470, 275, 650, 350, outline="black", width=1, fill="")
        # 10 Lineas verticales dentro del rectángulo 470, 275, 650, 350
        self.canvas.create_line(470, 275, 470, 350, width=1, fill="black")
        self.canvas.create_line(490, 275, 490, 350, width=1, fill="black")
        self.canvas.create_line(510, 275, 510, 350, width=1, fill="black")
        self.canvas.create_line(530, 275, 530, 350, width=1, fill="black")
        self.canvas.create_line(550, 275, 550, 350, width=1, fill="black")
        self.canvas.create_line(570, 275, 570, 350, width=1, fill="black")
        self.canvas.create_line(590, 275, 590, 350, width=1, fill="black")
        self.canvas.create_line(610, 275, 610, 350, width=1, fill="black")
        self.canvas.create_line(630, 275, 630, 350, width=1, fill="black")
        self.canvas.create_line(650, 275, 650, 350, width=1, fill="black")
        
        self.canvas.create_rectangle(400, 275, 470, 375, outline="black", width=1, fill="")
        
        self.canvas.create_text(500, 500, text="Sala", font=(None, 16, "bold"))
        self.canvas.create_text(800, 320, text="Cocina", font=(None, 8, "bold"))
        self.canvas.create_text(730, 150, text="Baño", font=(None, 11, "bold"))
        self.canvas.create_text(500, 250, text="Cuarto Principal", font=(None, 8, "bold"))
        self.canvas.create_text(890, 640, text="Puerta", font=(None, 16, "bold"))

        self.canvas.create_text(650, 20, text="Plano 2D", font=(None, 16, "bold"))

        self.canvas.create_rectangle(410, 560, 450, 640, outline="gray", width=1, fill="lightgray")

        self.insertar_imagen_canvas("images/planta1.png", 410, 570)
        self.insertar_imagen_canvas("images/sofa1.png", 340, 420, 200, 100, rotar=True)

        self.dibujar_sensores()

    def obtener_color(self, tipo, valor):
        if tipo == "Temperatura":
            # Azul (frío), Verde (templado), Amarillo (cálido), Rojo (calor)
            if valor < 10:
                return "#3A8DFF"  # Azul
            elif valor < 20:
                return "#4FFF8D"  # Verde
            elif valor < 30:
                return "#FFF700"  # Amarillo
            else:
                return "#FF5733"  # Rojo
        if tipo == "Humedad":
            # Marrón (muy seco), Amarillo (seco), Verde (óptimo), Azul (muy húmedo)
            if valor < 20:
                return "#A0522D"  # Marrón
            elif valor < 40:
                return "#FFF700"  # Amarillo
            elif valor < 70:
                return "#4FFF8D"  # Verde
            else:
                return "#3A8DFF"  # Azul
        if tipo == "Distancia":
            # Rojo (muy cerca), Naranja (cerca), Verde (lejos), Gris (muy lejos)
            if valor < 10:
                return "#FF5733"  # Rojo
            elif valor < 30:
                return "#FFA500"  # Naranja
            elif valor < 100:
                return "#4FFF8D"  # Verde
            else:
                return "#B0B0B0"  # Gris
        if tipo == "Luz":
            # Gris oscuro (muy poca luz), Azul (poca luz), Amarillo (media), Blanco (mucha luz)
            if valor < 50:
                return "#222222"  # Gris oscuro
            elif valor < 150:
                return "#3A8DFF"  # Azul
            elif valor < 250:
                return "#FFF700"  # Amarillo
            else:
                return "#FFFFFF"  # Blanco
        return "gray"

    def dibujar_sensores(self):
        self.canvas.delete("sensor")
        unidades = {
            "Temperatura": "°C",
            "Humedad": "%",
            "Distancia": "cm",
            "Luz": "lux"
        }
        for tipo, sensor in self.sensores.items():
            color = self.obtener_color(tipo, sensor["valor"])
            self.canvas.create_oval(sensor["x"]-20, sensor["y"]-20, sensor["x"]+20, sensor["y"]+20,
                                    fill=color, tags="sensor")
            # Formato de texto con unidad
            if tipo == "Distancia":
                texto = f"{tipo}: {sensor['valor']:.2f} {unidades[tipo]}"
            else:
                texto = f"{tipo}: {sensor['valor']:.0f} {unidades[tipo]}"
            self.canvas.create_text(sensor["x"], sensor["y"]-25,
                                    text=texto, font=(None, 9), tags="sensor")

    def recibir_datos(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("10.1.141.29", 5001))
                while True:
                    data = s.recv(1024)
                    datos = json.loads(data.decode("utf-8"))
                    for clave in self.sensores:
                        if clave in datos:
                            self.sensores[clave]["valor"] = datos[clave]
                    self.dibujar_sensores()
        except Exception as e:
            print("Error al conectarse al servidor:", e)

    def show_2d2st(self):
        self.clear()
        th_wall = 4
        self.sensores = self.sensores_2piso
        # Pared exterior (rectángulo con esquina diagonal)
        corners = [
            (400, 50),    # superior izquierda
            (800, 50),   # superior derecha
            (800, 580),  # punto medio en lado derecho
            (740, 650),   # vértice diagonal inferior derecho
            (400, 650)    # inferior izquierda
        ]

        ##SENSOOOOOORES
        

        # RECAMARAAA
        self.canvas.create_rectangle(440, 120, 550, 200, outline="black", width=1, fill="lightyellow")
        self.canvas.create_rectangle(440, 60, 470, 110, outline="black", width=1, fill="#F1D191")
        self.canvas.create_rectangle(440, 210, 470, 260, outline="black", width=1, fill="#F1D191")
        self.canvas.create_text(530, 80, text="Dormitorio", font=(None, 10), fill="black")
        self.canvas.create_text(760, 90 ,text="Ropero", font=(None, 10), fill="black")
        self.canvas.create_text(760, 300 ,text="Baño", font=(None, 10), fill="black")
        self.canvas.create_text(700, 500, text="Sala de estar", font=(None, 10), fill="black")

        self.canvas.create_line(430, 50, 430, 290, width=th_wall)
        self.canvas.create_line(400, 290, 550, 290, width=th_wall)
        self.canvas.create_line(600, 290, 610, 290, width=th_wall)
        self.canvas.create_line(610, 300, 610, 240, width=th_wall)
        self.canvas.create_line(610, 240, 800, 240, width=th_wall)
        self.canvas.create_line(670, 240, 670, 190, width=th_wall)
        self.canvas.create_line(670, 110, 670, 50, width=th_wall)
        self.canvas.create_line(610, 370, 800, 370, width=th_wall)
        self.canvas.create_line(610, 372, 610, 360, width=th_wall)

        self.canvas.create_rectangle(600, 290, 595, 240, outline="black", width=1, fill="")
        self.canvas.create_rectangle(610, 355, 670, 360, outline="black", width=1, fill="")



        # escaleras

        self.canvas.create_line(400, 370, 540, 370, width=1)
        self.canvas.create_line(540, 370, 540, 290, width=1)
        self.canvas.create_line(520, 370, 520, 290, width=1)
        self.canvas.create_line(500, 370, 500, 290, width=1)
        self.canvas.create_line(480, 370, 480, 290, width=1)
        self.canvas.create_line(460, 370, 460, 290, width=1)
        self.canvas.create_line(440, 370, 440, 290, width=1)
        self.canvas.create_line(420, 370, 420, 290, width=1)

        self.canvas.create_line(400, 365, 545, 365, width=1)
        self.canvas.create_line(540, 360, 540, 650, width=1)
        # 5 de separacion entre las lineas
        self.canvas.create_line(545, 365, 545, 650, width=1)


        self.canvas.create_rectangle(580, 55, 660, 45, outline="gray", width=1, fill="lightgray")
        self.canvas.create_rectangle(580, 655, 660, 645, outline="gray", width=1, fill="lightgray") 
        self.canvas.create_text(620, 20, text="Plano 2D Segundo Piso", font=(None, 16, "bold"))

        for i in range(len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % len(corners)]
            self.canvas.create_line(x1, y1, x2, y2, width=th_wall)

        self.dibujar_sensores()

    def show_3d(self):
        self.clear()
        # Cargar y mostrar la imagen 3d.webp a pantalla completa, manteniendo la relación de aspecto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "images", "3d.webp")
        img = Image.open(img_path)
        # Tamaño del canvas
        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()
        if ancho_canvas < 100 or alto_canvas < 100:
            ancho_canvas = self.root.winfo_screenwidth()
            alto_canvas = self.root.winfo_screenheight()
        # Mantener relación de aspecto
        img_w, img_h = img.size
        ratio = min(ancho_canvas / img_w, alto_canvas / img_h)
        nuevo_ancho = int(img_w * ratio)
        nuevo_alto = int(img_h * ratio)
        img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        # Centrar la imagen en el canvas
        x = (ancho_canvas - nuevo_ancho) // 2
        y = (alto_canvas - nuevo_alto) // 2
        self.canvas.create_image(x, y, image=img_tk, anchor=tk.NW)
        self.imagenes_tk = [img_tk]

    def show_references(self):
        self.clear()
        x, y = 50, 50
        for img in self.ref_images:
            self.canvas.create_image(x, y, image=img, anchor=tk.NW)
            x += img.width() + 20
        if not self.ref_images:
            self.canvas.create_text(400, 300, text="No se encontraron imágenes de referencia.",
                                    font=(None, 14), fill="gray")
        self.canvas.create_text(400, 20, text="Imágenes de Referencia", font=(None, 16, "bold"))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HomePlanner()
    app.run()
