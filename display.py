import pygame
import os
import time
import threading


DEFAULT_DRIVERS = ('fbcon', 'directfb', 'svgalib', 'Quartz')
DEFAULT_SIZE = (800, 480)
DEFAULT_SCREEN = 'resizable'

class DisplayDriver:

        def __init__(self, drivers=DEFAULT_DRIVERS, size=DEFAULT_SIZE, screen_type=DEFAULT_SCREEN, borders=(5, 5),
                 border_width=3, line_color=(255, 255, 255), font='freesans', font_color=(255, 255, 255)): #,icons=ICON_DICTIONARY):
                """DisplayDriver class is the class that build the base display for use in the weather
                app.  Argument descriptions: drivers is a tuple of strings with available SDL_VIDEODRIVER
                environmental varaibles; size is a tuple of two integers describing the x, y size of the
                screen; screen_type is a string value that corresponds to the pygame constants for
                dispay.set_mode
                """

                formats = {'no_frame': pygame.NOFRAME, 'full_screen': pygame.FULLSCREEN, 'double_buff': pygame.DOUBLEBUF,
                        'hw_surface': pygame.HWSURFACE, 'open_GL': pygame.OPENGL, 'resizable': pygame.RESIZABLE}

                self._display_instance = None
                self._drivers = drivers
                self._size = size
                self._borders = borders
                self._border_width = border_width
                self._line_color = line_color
                self._font = font
                self._font_color = font_color
                self._format = formats[screen_type]
                # self._icons = icons
                # self._base_dir = os.getcwd() + ICON_BASE_DIR
                self._scale_icons = True
                self._xmax = self._size[0] - self._borders[0]
                self._ymax = self._size[1] - self._borders[1]
                self._av = 1
                self._av_time = 1
                self._screen = None
                self._blits = []
                self.running = True
                self.current_date = None

        def update_display(self):
                try:
                        self.__draw_frames()
                        self.__display_datetime()
                        self.__render_screen()
                        pygame.display.update()
                        print("Display update complete")
                except AssertionError as err:
                        print("Update Error + {}".format(str(err)))

        
        def run(self, run_delay=209, interval=60):
                self.display_start()
                self.main_loop(run_delay)
                pygame.quit()

        def main_loop(self, run_delay):
                cnt = run_delay

                while self.running:
                        pygame.time.wait(1000)
                        self.update_display()
                        cnt += 1
                        if cnt >= run_delay:
                                try:
                                        #self.update_current_data()
                                        cnt = 0
                                except ConnectionError as e:
                                        print("No connection on current data update")
                                        cnt = run_delay
                        if time.strftime("%d/%m") != self.current_date:
                                try:
                                        #self.update_daily_data()
                                        self.current_date = time.strftime("%d/%m")
                                except ConnectionError as e:
                                        self.current_date = None
                                        print("No connection on daily data update.")
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        self.running = False
                                elif event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_ESCAPE:
                                                self.running = False

        def __display_datetime(self):
                th = 0.07     # Time Text Height
                sh = 0.03     # Seconds Text Height
                dh = 0.06     # Date Text Height
                dt_y = 13     # Date Y Position
                tm_y = 10     # Time Y Position
                tm_y_sm = 15  # Time Y Position Small

                tfont = pygame.font.SysFont(self._font, int(self._ymax * th), bold=1)  # Time Font
                dfont = pygame.font.SysFont(self._font, int(self._ymax * dh), bold=1)  # Date Font
                sfont = pygame.font.SysFont(self._font, int(self._ymax * sh), bold=1)  # Small Font for Seconds

                tm1 = time.strftime("%H:%M", time.localtime())  # Time String
                tm2 = time.strftime("%S", time.localtime())     # Seconds String
                dt1 = time.strftime("%d %b %y").upper()         # Date String

                # Build the Date / Time
                rtm1 = tfont.render(tm1, True, self._font_color)
                (tx1, ty1) = rtm1.get_size()
                rtm2 = sfont.render(tm2, True, self._font_color)
                (tx2, ty2) = rtm2.get_size()
                rdt1 = dfont.render(dt1, True, self._font_color)
                (dx1, dy1) = rdt1.get_size()

                tp = self._xmax / 2 - (tx1 + tx2) / 2
                dp = self._xmax - (dx1 + (self._borders[1] * 2))
                self._screen.blit(rtm1, (tp, tm_y))
                self._screen.blit(rtm2, (tp + tx1 + 3, tm_y_sm))
                self._screen.blit(rdt1, (dp, dt_y))
        
        def display_start(self):
                """display_start is the main initializer for the display it makes calls to many other
                internal functions in order do build the dispay as defined in the initialization of the
                DispayDriver class."""

                try:
                        self.__get_driver()
                        self.__draw_screen()
                        print("Display setup completed")

                except AssertionError as err:
                        print(str(err))
                        quit()

        def __append_blits(self, blits):

                for blit in blits:
                        self._blits.append(blit)

        def __get_driver(self):
                has_driver = False
                for driver in self._drivers:
                        if not os.getenv('SDL_VIDEODRIVER'):
                                os.putenv('SDL_VIDEODRIVER', driver)
                        try:
                                pygame.display.init()
                        except pygame.error:
                                print('Driver: {} not loaded.'.format(driver))
                                continue
                        print('Driver: {} used.'.format(driver))
                        has_driver = True
                        break

                if not has_driver:
                        raise AssertionError('No video driver available for use!')

        def __render_screen(self):
                for _ in range(len(self._blits)):
                        blit = self._blits.pop() # pop off each item once drawn to allow for updates to display
                        self._screen.blit(blit[0], blit[1])

        def __draw_screen(self):
                """This function is intended to be used by the display_start function.
                It attempts to build the blank screen and raises an error if it fails."""

                self._screen = pygame.display.set_mode(self._size, self._format)

                if not self._screen:
                        raise AssertionError('Screen not defined')

                self._screen.fill((0, 0, 0))
                pygame.font.init()

                # Mouse hider -- Comment the next line to see mouse over the display
                pygame.mouse.set_visible(0)
                pygame.display.update()

        def __draw_frames(self):
                """This function should be called by the display_start function only. It renders the frames for the display"""
                xmin = self._borders[0]
                ymin = self._borders[1]
                xmax = self._xmax
                ymax = self._ymax
                line_width = self._border_width

                # Horizontal line settings
                hz = (0.1, 0.5, 0.58)

                # Vertical line settings
                vt = (0.33, 0.66, 0.2, 0.4, 0.6, 0.8)

                self._screen.fill((0, 0, 0))

                # Draw Screen Border
                pygame.draw.line(self._screen, self._line_color, (xmin, xmin), (xmax, xmin), line_width)  # Top
                pygame.draw.line(self._screen, self._line_color, (xmin, xmin), (xmin, ymax), line_width)  # Left
                pygame.draw.line(self._screen, self._line_color, (xmin, ymax), (xmax, ymax), line_width)  # Bottom
                pygame.draw.line(self._screen, self._line_color, (xmax, ymin), (xmax, ymax), line_width)  # Right Edge

                # Draw Inner Frames
                # Horizontal lines (1, 2, 3)
                for h in hz:
                        pygame.draw.line(self._screen, self._line_color, (xmin, ymax * h), (xmax, ymax * h), line_width)

                # Vertical lines (1, 2)
                for j in range(2):
                        v = vt[j]
                        pygame.draw.line(self._screen, self._line_color, (xmax * v, ymax * hz[2]),
                                        (xmax * v, ymax * hz[0]), line_width)

                # Vertical lines (3 - 6)
                for j in range(2, len(vt)):
                        v = vt[j]
                        pygame.draw.line(self._screen, self._line_color, (xmax * v, ymax), (xmax * v, ymax * hz[2]), line_width)
