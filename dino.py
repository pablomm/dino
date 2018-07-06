#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# File with the chrome driver for selenium
# The last compatible release can be downloaded
# in http://chromedriver.chromium.org/downloads
driverPath = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "chromedriver")

# Default URL to the dino game
gameURL = "chrome://dino/"

# ID added to the canvas
canvasID = "runner-canvas"


class Dino:
    """Interface between the browser and python
    Provide the methods needed to known the state of the game
    and control the T-Rex Runner.
    """

    def __init__(self, driver=None, url=None, mute=True):
        """Dino constructor.

        Args:
            driver (webdriver, optional): Initialized selenium webdriver
            url (str, optional): Alternative game url
            mute (bool, optional): Mute the browser
        """
        self._driver = driver
        self.url = gameURL if url == None else url
        self._mute = mute

    def _setup(self):
        """Initialize the driver and the game settings
        """

        # Loads the driver if it is not provided
        if self._driver == None:
            options = Options()
            options.add_argument("disable-infobars")
            if self._mute == True:
                options.add_argument("--mute-audio")

            self._driver = webdriver.Chrome(driverPath, chrome_options=options)

        # Go to the dino page
        self._driver.get(self.url)

        # Create id for canvas for faster selection from DOM
        # See https://github.com/Paperspace/DinoRunTutorial
        self._driver.execute_script(
            "document.getElementsByClassName('runner-canvas')[0].id = '{}'".format(canvasID))

        # Add Shift key (code 16) to the duck action to avoid selenium
        # limitations with the key_down function
        self._driver.execute_script(
            "Runner.keycodes['DUCK'] = {'40' : 1, '16' : 1};")

        # Width of the Pterodactyl used for the duck
        self.pterodactylx = int(self.getProperty(
            "Runner.spriteDefinition.LDPI.PTERODACTYL.x"))

        # Configuration params of the game
        self.gameConfig = self.getProperty("Runner.config")

        # Rest of initialization stuff
        self.body = self._driver.find_element(By.TAG_NAME, "body")
        self.canvas = self._driver.find_element(By.ID, canvasID)

    def start(self, delay=3.):
        """Start the game.

        Args:
            delay (float, optional): Seconds waited after start the game

        """
        # Initialize the game
        self._setup()

        # Jump to start the game
        self.jump()

        # Initial delay after start the game without action
        time.sleep(delay)

        return self

    def jump(self):
        """Make the dino jump."""

        self.body.send_keys(Keys.SPACE)

    def duck(self, delay=None):
        """Make the dino duck.
            TODO: Adjust default delay to the current speed.

            Args:
                delay (float, optional): Seconds ducking
        """

        if delay == None:
            delay = (self.pterodactylx+20)/self.speed
            delay = .5

        ActionChains(self._driver).key_down(Keys.SHIFT).perform()
        time.sleep(delay)
        ActionChains(self._driver).key_up(Keys.SHIFT).perform()

    def cancelJump(self):
        self.body.send_keys(Keys.ARROW_DOWN)

    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")

    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")

    def end(self):
        try:
            self._driver.close()
        except:
            pass

    def getProperty(self, property):
        """Execute JS code to get the property requested, i.e."""
        return self._driver.execute_script("return {}".format(property))

    @property
    def crashed(self):
        """True if the dino is crashed"""
        return self.getProperty("Runner.instance_.crashed")

    @property
    def playing(self):
        """True if the dino is playing"""
        return self.getProperty("Runner.instance_.playing")

    @property
    def score(self):
        """Return the score"""
        score_array = self.getProperty("Runner.instance_.distanceMeter.digits")
        score = ''.join(score_array)
        return int(score)

    @property
    def speed(self):
        """Return the speed"""
        return float(self.getProperty("Runner.instance_.currentSpeed"))

    @property
    def image(self):
        """Return the dino image png encoding in base64"""
        return self._driver.execute_script(
            "canvasRunner = document.getElementById('runner-canvas');\
            return canvasRunner.toDataURL().substring(22)")

    @property
    def obstacles(self):
        print("Obstacles")
        """Return a tuple with the distance of each object"""
        return self._driver.execute_script("obst = [];\
                                           Runner.instance_.horizon.obstacles.forEach(\
                                           function(e){\
                                           e = Object.assign({},e);\
                                           delete e.canvasCtx;\
                                           obst.push(e)});\
                                           return obst")

    @property
    def tRex(self):
        """Extract all the info needed to known the state of the game"""
        return self._driver.execute_script("trex = Object.assign({},Runner.instance_.tRex);\
                                           delete trex.canvas;\
                                           delete trex.canvasCtx;\
                                           delete trex.currentAnimFrames;\
                                           delete trex.config;\
                                           return trex")


if __name__ == '__main__':

    import random

    random.seed()
    dino = Dino().start()

    # Dummy random behaviour
    try:
        while True:
            random.choice(10*[dino.jump] + [dino.duck, dino.cancelJump])()
            time.sleep(0.6)

    except:
        dino.end()
