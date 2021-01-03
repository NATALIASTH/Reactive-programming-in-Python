from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import rx
import rx.operators as ops
from io import BytesIO


class App():


    def __init__(self):
        self.window = Tk()
        self.window.title('Aplicación Gráfica!')
        #creo la ventana y pongo resizable en true para que se pueda ampliar si la foto es demasiado grande
        self.window.geometry('800x400')
        self.window.resizable(True, True)

        Label(text='URL a procesar!').grid(column=0, row=0)
        #creamos el hueco donde vamos a escribit la url,con su grid y su boton que llama a la funcion buttonentry
        self.entry = Entry()
        self.entry.grid(column=4, row=0)
        Button(text='Buscar', command=self.buttonEntry).grid(column=4, row=1, columnspan=2)
        #creamos la list box
        self.listbox = Listbox()
        self.listbox.grid(column=0, row=3)
        self.listbox.bind("<Double-1>", self.onselect)
        #creamos la progressbar
        self.barrita = Progressbar()
        self.barrita.grid(column=6, row=5)
        #label progress para el contador de imagenes
        self.label_progress_bar = Label()
        self.label_progress_bar.grid(column=7, row=9)
        #Imagen

        #creamos el label donde aparecera la imagen
        self.labelimage = Label(self.window)
        self.labelimage.grid(column=6,row=3)

        self.window.mainloop()
    #llamamos a onselect desde bind de la listbox y le pasamos el  parametro y el evento
    def onselect(self, evt):
        #y ponemos que con si hay curseelection recoja el elemento y llame a showimage para mostrarlo pansandole el valor
        element=self.listbox.curselection()
        value=self.listbox.get(element)
        self.showimage(value)

    #lo llamamos desde buttonentry cuando el observer lo llama e insertamos en la listbox el array
    def updateList(self, arr):
        print("El array tiene....")
        print(arr)
        self.listbox.insert(END, arr)

    #Una vez se llama a esta funcion para el valor que le han pasado hace un request para ver los bytes , lo abre y guarda el numero de bytes en nbytes y la muestra en el label con pillow de tkinter
    def showimage(self, image):
        print("HOLA:" ,image)
        nbytes = Image.open(BytesIO(requests.get(image).content))
        newImagePIL = ImageTk.PhotoImage(image=nbytes)
        self.labelimage.configure(image=newImagePIL)
        self.labelimage.image = newImagePIL



    #descargamos las imagenes de forma asincrona y utilizando aiohttp, guardamos la info obtenida en response y seguidamente el html en la variable html
    #seguidamente con beautifulsoup meto la variable html y le pido que encuentre los tags de img que terminen con jpg y png
    #contador de progressbar para contar la imagenes
    #inicializo el observer con from_ a lista de self.img_src
    async def main(self, m):

        async with aiohttp.ClientSession() as session:
            async with session.get(m) as response:
                html = await response.text()
                # print("Body:", html, "...")
                soup = BeautifulSoup(html, 'lxml')
                imagenes = soup.find_all('img', src=True)
                image_src = [x['src'] for x in imagenes]

                self.image_src = [x for x in image_src if x.endswith('.jpg') or x.endswith('.png')]
                self.contador = len(self.image_src)
                self.label_progress_bar.configure(text='Se han encontrado ' + str(self.contador) + ' imagenes')
                self.label_progress_bar.update()

                self.Obs = rx.from_(self.image_src).pipe(
                    ops.map(lambda a: a, )
                )

    #se llama desde el boton de buscar, coge la url que le introducimos, se suscribe con el observer en esta funcion y si funciona llama a updatelist
    def buttonEntry(self):
        url_usr = self.entry.get()
        print(url_usr)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(url_usr))
        self.Obs.subscribe_(
            on_next=lambda i: self.updateList(i),
            on_completed=lambda: print("Hecho"),
            on_error=lambda e: print("error {0}".format(e)), )
        #aumentamos barrita(el progressbar)cada vez que descargamos una imagen
        incremento = (1 / self.contador) * 100
        self.barrita.step(incremento)
        self.barrita.update_idletasks()
        if self.barrita['value'] < 100:
            self.barrita['value'] = 100


if __name__ == '__main__':
    App()