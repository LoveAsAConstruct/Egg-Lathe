from structure import *
from commands import *
import pygame
import pygame.font
import serial
class MainWindow:
    def __init__(self, queue):
        self.queue = queue
        pygame.init()
        self.window = pygame.display.set_mode((700,500))
        pygame.display.set_caption("Egg Lathe")
        self.previewWindow = pygame.Surface((400,400))
        self.executeButton = Button("Execute",(450,25), (100, 50), self.executeButtonClicked)
        self.consoleText = ""
        self.looping = None
        self.running = True
        self.commandtime = 663723456
        while self.running:
            self.loop()
        pygame.quit()
        
    def executeButtonClicked(self):
        try:
            ser = serial.Serial('/dev/cu.usbmodem101', 9600, timeout=1)
        except serial.SerialException:
            print("The port is not available")
            self.consoleText = "Cannot connect to port /dev/cu.usbmodem101"
        else:
            self.consoleText = "Connecting..."
            print("Connecting...")
            time.sleep(1)  # Allow time for the connection to establish
            self.consoleText = "Connected! Executing..."
            self.queue.execute(ser,window = self)
        
    def loop(self):
        self.updateEvents()
        self.draw()
            
    def updateEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.executeButton.handle_event(event)
                
    def draw(self):
        self.queue.previewPygame(surface = self.previewWindow,executionIndex = self.looping)
        self.window.fill((255,255,255))
        self.window.blit(self.previewWindow, (25,25))
        self.executeButton.draw(self.window)
        consoleText = pygame.font.Font(None,25).render(self.consoleText,True,(0,0,0))
        self.window.blit(consoleText,(25,425))
        consoleText = pygame.font.Font(None,25).render(f"ETA: {round(((len(self.queue.queue)-self.progress())*self.commandtime)/1000000000)} seconds",True,(0,0,0))
        self.window.blit(consoleText,(25,450))
        pygame.display.flip()
    
    def progress(self):
        if self.looping == None:
            return 0
        else:
            return self.looping

class Button:
    def __init__(self, text, position, size, callback, font_size=30, text_color=(255, 255, 255), btn_color=(0, 0, 255), hover_color = None):
        """
        Initializes a button.
        
        Parameters:
        - text: The text to display on the button.
        - position: A tuple for the position of the button (x, y).
        - size: A tuple for the size of the button (width, height).
        - callback: The function to execute when the button is clicked.
        - font_size: The size of the text font.
        - text_color: The color of the text (default is white).
        - btn_color: The color of the button (default is blue).
        """
        self.text = text
        self.position = position
        self.size = size
        self.callback = callback
        self.font_size = font_size
        self.text_color = text_color
        self.btn_color = btn_color
        if hover_color == None:
            self.hover_color = (round(btn_color[0]/2),round(btn_color[1]/2),round(btn_color[2]/2))
        else:
            self.hover_color = hover_color
            
        self.hover = False
        
        self.font = pygame.font.Font(None, self.font_size)
        self.rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    def draw(self, screen):
        """Draws the button on the specified screen."""
        if self.hover:
            color = self.hover_color
        else:
            color = self.btn_color
        pygame.draw.rect(screen, color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Handles the event (to check if the button is clicked)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hover = True
            else:
                self.hover = False

