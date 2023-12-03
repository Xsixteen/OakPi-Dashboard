import pygame
import os
import time
import datetime
import threading
import weather
import pytemperature
import gatestatus
import settings
import os
import power

DEFAULT_DRIVERS = ('fbcon', 'directfb', 'svgalib', 'Quartz', 'x11')
DEFAULT_SIZE = (800, 480)
DEFAULT_SCREEN = 'resizable'

class DisplayDriver:

        def __init__(self, drivers=DEFAULT_DRIVERS, size=DEFAULT_SIZE, screen_type=DEFAULT_SCREEN, borders=(5, 5),
                 border_width=3, line_color=(255, 255, 255), font='freesans', font_color=(255, 255, 255)):
                """DisplayDriver class is the class that build the base display for use in the weather
                app.  Argument descriptions: drivers is a tuple of strings with available SDL_VIDEODRIVER
                environmental varaibles; size is a tuple of two integers describing the x, y size of the
                screen; screen_type is a string value that corresponds to the pygame constants for
                dispay.set_mode
                """

                formats = {'no_frame': pygame.NOFRAME, 'full_screen': pygame.FULLSCREEN, 'double_buff': pygame.DOUBLEBUF,
                        'hw_surface': pygame.HWSURFACE, 'open_GL': pygame.OPENGL, 'resizable': pygame.RESIZABLE}

                self.weatherObj = weather.Weather()
                self.gatestatusObj = gatestatus.GateStatus();
                self.powerObj = power.Power()
                self._display_instance = None
                self._drivers = drivers
                self._size = size
                self._borders = borders
                self._border_width = border_width
                self._line_color = line_color
                self._font = font
                self._font_color = font_color
                self._format = formats[screen_type]
                self._scale_icons = True
                self._xmax = self._size[0] - self._borders[0]
                self._ymax = self._size[1] - self._borders[1]
                self._av = 1
                self._av_time = 1
                self._screen = None
                self._blits = []
                self._refresh_icon = None
                self.running = True
                self.current_date = None

        def update_display(self):
                try:
                        self.__draw_frames()
                        self.__display_datetime()
                        self.__display_outdoortemp()
                        self.__display_forecast()
                        self.__render_screen()
                        self.__render_gateimage()
                        self.__draw_buttons()
                        self.__display_power()
                        pygame.display.update()
                        print("Display update complete")
                except AssertionError as err:
                        print("Update Error + {}".format(str(err)))

        def __render_gateimage(self):
                gateimg = pygame.image.load('./images/latest_image.jpg')
                gateimg_small = pygame.transform.scale(gateimg, (320, 180))
  
                self._screen.blit(gateimg_small,(int((self._xmax*0.33+5)),int(self._borders[0]+45)))

        def __draw_buttons(self):
                refresh = pygame.image.load('./icons/refresh.png')
                self._refresh_icon = pygame.transform.scale(refresh, (64, 64))
                self._screen.blit(self._refresh_icon,(int((self._xmax*0.33+350)),int(self._borders[0]+150)))

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
                                elif event.type == pygame.MOUSEBUTTONUP:
                                        print("Updating Image")
                                        os.system("python3 " + settings.blink_app + " ./images/latest_image.jpg")

        def __display_forecast(self):
                forecastobject = self.weatherObj.getForecast()
                for i in range(len(forecastobject)):
                        temprange = pygame.font.SysFont(self._font, int(self._ymax * 0.05), bold =1)
                        rendertemprange = temprange.render(str(int(pytemperature.k2f(float(forecastobject[i]["high"]))))+"/"+str(int(pytemperature.k2f(float(forecastobject[i]["low"])))), True, self._font_color)
                        displaytime = datetime.datetime.fromtimestamp(float(forecastobject[i]["date"])).strftime('%a')
                        dayofweek = pygame.font.SysFont(self._font, int(self._ymax * 0.05), bold =1)
                        renderdayofweek = dayofweek.render(displaytime, True, self._font_color)
                        iconref = str(forecastobject[i]["icon"])
                        if iconref in settings.icon_map:
                                icon = pygame.image.load_extended(settings.ICON_BASE_DIR + settings.icon_map[iconref])
                                self._screen.blit(icon, ((self._xmax*0.4)+(self._xmax*0.2)*(i)+50,int(self._ymax - 130)))

                        self._screen.blit(rendertemprange, ((self._xmax*0.4)+(self._xmax*0.2)*(i)+50,int(self._ymax - 50)))
                        self._screen.blit(renderdayofweek, ((self._xmax*0.4)+(self._xmax*0.2)*(i)+50,int(self._ymax - 180 )))

                
                sunsetText = pygame.font.SysFont(self._font, int(self._ymax * 0.05), bold=1)

                sunsetTime = time.strftime('%-l:%M', time.localtime(self.weatherObj.getSunset()))

                renderSunset = sunsetText.render("Sunset: " + sunsetTime + " pm", True, self._font_color)

                (rtx, rty) = renderSunset.get_size()
                self._screen.blit(renderSunset, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax*0.1)+65))

        def __display_gatestatus(self):
                banner = pygame.font.SysFont(self._font, int(self._ymax * 0.07), bold=1)
                renderbanner = banner.render("Gate Status", True, self._font_color)
                (rtx, rty) = renderbanner.get_size()
                
                GATESTATUS = self.gatestatusObj.getGateStatus();
                gatestatus = pygame.font.SysFont(self._font, int(self._ymax * 0.07), bold = 1)
                if GATESTATUS["gatestatus"] == '"CLOSE"' :
                        commonText = "Closed"
                else:
                        commonText = "Open"
                rendergatestatus = gatestatus.render(commonText, True, self._font_color)
                (rgtx, rgty) = rendergatestatus.get_size()

                timestatus = pygame.font.SysFont(self._font, int(self._ymax * 0.04), bold=1)
                rendertimestatus = timestatus.render("at " +datetime.datetime.fromtimestamp(float(GATESTATUS["time"])/1000).strftime('%I:%M %p on %b %-d'), True, self._font_color)
                (rtsx, rtsy) = rendertimestatus.get_size()
                
                self._screen.blit(renderbanner, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax*0.1)+5))
                self._screen.blit(rendergatestatus, (self._borders[0]+(self._xmax*0.16-(rgtx/2)), int(self._ymax*0.25)))
                self._screen.blit(rendertimestatus, (self._borders[0]+(self._xmax*0.16-(rtx/2)-8), int(self._ymax*0.25)+65))
               
        def __display_outdoortemp(self):
                tempK = self.weatherObj.getCurrentWeather()
                tempF = int(pytemperature.k2f(float(tempK)))
                font = pygame.font.SysFont(self._font, int(self._ymax*(0.5-0.15)*0.9), bold=1)
                temp = font.render(str(tempF), True, self._font_color)
                (tx,ty) = temp.get_size()
                ffont = pygame.font.SysFont(self._font, int(self._ymax*(0.5-0.15)*0.5), bold=1)
                ftext = ffont.render(chr(0x2109), True, self._font_color)
                (ftx, fty) = ftext.get_size()	

                text = pygame.font.SysFont(self._font, int(self._ymax * 0.07), bold=1)
                rendertext = text.render("Outdoor", True, self._font_color)
                (rtx, rty) = rendertext.get_size()
	
                self._screen.blit(rendertext, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax - ty - 30)))
                self._screen.blit(temp, (self._borders[0]+30,int(self._ymax - ty)))
                self._screen.blit(ftext, (self._borders[0]+20+tx+15, int(self._ymax - ty + 5)))
                
                # Hold off for now
                # precip = pygame.font.SysFont(self._font, int(self._ymax * 0.07), bold=1)
                # renderPrecip = precip.render("Precipitation:", True, self._font_color)
                # (rtx, rty) = renderPrecip.get_size()
                #self._screen.blit(renderPrecip, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax*0.1)+5))

        def __display_power(self):
                self.power = self.powerObj.getCurrentPower()
                powerText = pygame.font.SysFont(self._font, int(self._ymax * 0.05), bold=1)
                powerBanner = pygame.font.SysFont(self._font, int(self._ymax * 0.05), bold=1)

                if(int(self.power.currentPower) > 1000 ) :
                        kilowatts = str(round((self.power.currentPower/1000), 2))
                        renderPowerText = powerText.render(kilowatts + " KW", True, self._font_color)
                else:
                        watts = int(self.power.currentPower)
                        renderPowerText = powerText.render(str(watts) + " Watts", True, self._font_color)
                stalePower = int(time.time()) - (60 * 10)
                print("Current Power API Epoch: " + str(self.power.currentPowerEpochTimeSeconds) + " will be stale after: " + str(stalePower))
                if int(self.power.currentPowerEpochTimeSeconds) < stalePower :
                        renderPowerText = powerText.render(" - ", True, self._font_color)
                        print("Power API is stale")

                renderPowerBanner = powerBanner.render("Power Usage:", True, self._font_color)
                (rtx, rty) = renderPowerBanner.get_size()
                self._screen.blit(renderPowerBanner, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax*0.1)+5))

                (rtx, rty) = renderPowerText.get_size()
                self._screen.blit(renderPowerText, (self._borders[0]+(self._xmax*0.16-(int(rtx/2))), int(self._ymax*0.1)+30))

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

                tm1 = time.strftime( "%a, %b %d   %I:%M", time.localtime())
                tm2 = time.strftime( "%S", time.localtime())
                tm3 = time.strftime( " %P", time.localtime())


                # Build the Date / Time
                rtm1 = tfont.render(tm1, True, self._font_color)
                (tx1, ty1) = rtm1.get_size()
                rtm2 = sfont.render(tm2, True, self._font_color)
                (tx2, ty2) = rtm2.get_size()
                rtm3 = tfont.render(tm3, True, self._font_color)
                (tx3, ty3) = rtm3.get_size()

                tp = self._xmax / 2 - (tx1 + tx2) / 2
                self._screen.blit(rtm1, (tp, tm_y))
                self._screen.blit(rtm2, (tp + tx1 + 3, tm_y_sm))
                self._screen.blit(rtm3, (tp+tx1+tx2, tm_y))
        
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
                vt = (0.33, 0.66,0.4, 0.6, 0.8)

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
                for j in range(1):
                        v = vt[j]
                        pygame.draw.line(self._screen, self._line_color, (xmax * v, ymax * hz[2]),
                                        (xmax * v, ymax * hz[0]), line_width)

                # Vertical lines (3 - 6)
                for j in range(2, len(vt)):
                        v = vt[j]
                        pygame.draw.line(self._screen, self._line_color, (xmax * v, ymax), (xmax * v, ymax * hz[2]), line_width)
