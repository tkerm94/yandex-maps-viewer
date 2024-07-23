import math
import os
import sys

import requests

from settings import *
from ui import UI


class App:
    def __init__(self):
        self.map_file = "map.png"
        self.coords = [-79.394073, 43.664936]
        self.scale = 12
        self.changed = False
        self.screen = pygame.display.set_mode(RES)
        self.map_rect = pygame.Rect(GAP, GAP * 2 + UI_INPUT_HEIGHT, *MAP_SIZE)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.point = ""
        self.address = ""
        self.postcode = ""
        self.postcode_added = False
        self.mode = 0
        self.modes = ["map", "sat,skl", "sat"]
        self.ui = UI(self.screen, self.font)

    def lonlat_distance(self, a, b):
        degree_to_meters_factor = 111 * 1000
        a_lon, a_lat = a
        b_lon, b_lat = b
        radians_lattitude = math.radians((a_lat + b_lat) / 2.0)
        lat_lon_factor = math.cos(radians_lattitude)
        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor
        distance = math.sqrt(dx * dx + dy * dy)
        return distance

    def get_biz(self, point):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        search_params = {
            "apikey": os.getenv("SEARCH_APIKEY"),
            "text": "organization",
            "lang": "en_US",
            "ll": point,
            "type": "biz",
        }
        response = requests.get(search_api_server, params=search_params)
        if not response:
            return
        response = response.json()
        organizations = response["features"]
        if not organizations:
            return
        for organization in organizations:
            org_address = organization["properties"]["CompanyMetaData"]["address"]
            org_coords = organization["geometry"]["coordinates"]
            distance = self.lonlat_distance(
                list(map(float, point.split(","))), org_coords
            )
            if distance <= 50:
                self.address = org_address
                self.point = ",".join(map(str, org_coords)) + ",pm2rdm"
                return

    def get_point(self, toponym_to_find, point=False):
        geocoder_params = {
            "apikey": os.getenv("GEOCODER_APIKEY"),
            "geocode": toponym_to_find,
            "lang": "en_US",
            "format": "json",
        }
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            return False
        response = response.json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"]
        if not toponym:
            return False
        toponym = toponym[0]["GeoObject"]
        address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]
        self.address = address["formatted"]
        if "postal_code" in address.keys():
            self.postcode = address["postal_code"]
            if self.postcode_added:
                self.address = f"{self.address}, {self.postcode}"
        if not point:
            self.point = ",".join(toponym["Point"]["pos"].split()) + ",pm2rdm"
            self.coords = list(map(float, (toponym["Point"]["pos"].split())))
        else:
            self.point = toponym_to_find + ",pm2rdm"
        return True

    def get_map(self):
        coords = ",".join(map(str, self.coords))
        map_params = {
            "ll": coords,
            "z": self.scale,
            "pt": self.point,
            "l": self.modes[self.mode],
            "lang": "en_US",
        }
        map_api_server = "http://static-maps.yandex.ru/1.x"
        response = requests.get(map_api_server, params=map_params)
        return response

    def process_click(self, event):
        if event.button == 1:
            button = self.ui.check_click(event.pos)
            if button == "mode":
                self.mode = (self.mode + 1) % len(self.modes)
                self.changed = True
            elif button == "search":
                self.postcode = ""
                ok = self.get_point(self.ui.input_text)
                if not ok:
                    self.address = "some error occured"
                self.ui.input_text = ""
                self.changed = True
            elif button == "clear":
                self.point = ""
                self.address = ""
                self.postcode = ""
                self.changed = True
            elif button == "postcode" and self.postcode:
                if not self.postcode_added:
                    self.address = f"{self.address}, {self.postcode}"
                    self.postcode_added = True
                else:
                    self.address = ",".join(self.address.split(",")[:-1])
                    self.postcode_added = False
                self.changed = True
            elif self.map_rect.collidepoint(event.pos):
                lat_changed, lon_changed = False, False
                x_diff = event.pos[0] - self.map_rect.centerx
                x_diff = 360 / (2 ** (self.scale + 8)) * x_diff
                new_lat = self.coords[0] + x_diff
                if -180 <= new_lat <= 180:
                    lat_changed = True
                y_diff = self.map_rect.centery - event.pos[1]
                y_diff = 180 / (2 ** (self.scale + 8)) * y_diff
                new_lon = self.coords[1] + y_diff
                if -85 <= new_lon <= 85:
                    lon_changed = True
                if lat_changed and lon_changed:
                    coords = f"{new_lat},{new_lon}"
                    self.postcode = ""
                    ok = self.get_point(coords, True)
                    if not ok:
                        self.address = "some error occured"
                    self.changed = True
        elif event.button == 3 and self.map_rect.collidepoint(event.pos):
            lat_changed, lon_changed = False, False
            x_diff = event.pos[0] - self.map_rect.centerx
            x_diff = 360 / (2 ** (self.scale + 8)) * x_diff
            new_lat = self.coords[0] + x_diff
            if -180 <= new_lat <= 180:
                lat_changed = True
            y_diff = self.map_rect.centery - event.pos[1]
            y_diff = 180 / (2 ** (self.scale + 8)) * y_diff
            new_lon = self.coords[1] + y_diff
            if -85 <= new_lon <= 85:
                lon_changed = True
            if lat_changed and lon_changed:
                coords = f"{new_lat},{new_lon}"
                self.postcode = ""
                self.address = ""
                self.point = ""
                self.get_biz(coords)
                self.changed = True

    def process_input(self, event):
        if event.key == pygame.K_PAGEUP:
            if self.scale < 21:
                self.scale += 1
                self.changed = True
        if event.key == pygame.K_PAGEDOWN:
            if self.scale > 0:
                self.scale -= 1
                self.changed = True
        if event.key in (pygame.K_DOWN, pygame.K_UP):
            diff = 180 / (2 ** (self.scale + 8)) * 450
            if event.key == pygame.K_DOWN:
                new_lon = self.coords[1] - diff
            else:
                new_lon = self.coords[1] + diff
            if -85 <= new_lon <= 85:
                self.coords[1] = new_lon
                self.changed = True
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            diff = 360 / (2 ** (self.scale + 8)) * 600
            if event.key == pygame.K_LEFT:
                new_lat = self.coords[0] - diff
            else:
                new_lat = self.coords[0] + diff
            if -180 <= new_lat <= 180:
                self.coords[0] = new_lat
                self.changed = True

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os.remove(self.map_file)
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.ui.active_input:
                    self.ui.process_input(event)
                else:
                    self.process_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.process_click(event)

    def update(self):
        if self.changed:
            self.changed = False
            response = self.get_map()
            with open(self.map_file, "wb") as file:
                file.write(response.content)
        img = pygame.image.load(self.map_file).convert_alpha()
        rect_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(
            rect_img, (255, 255, 255), (0, 0, *img.get_size()), border_radius=5
        )
        img.blit(rect_img, (0, 0), None, pygame.BLEND_RGBA_MIN)
        self.screen.fill(UI_BG_COLOR)
        self.screen.blit(img, (GAP, GAP * 2 + UI_INPUT_HEIGHT))
        self.ui.render(pygame.mouse.get_pos())
        text = self.font.render(self.address, True, UI_INPUT_TEXT_COLOR)
        rect = pygame.Rect(
            GAP, HEIGHT - UI_ADDRESS_HEIGHT - GAP, WIDTH - 2 * GAP, UI_ADDRESS_HEIGHT
        )
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def run(self):
        response = self.get_map()
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        while True:
            self.check_events()
            self.update()
            self.clock.tick(self.fps)
            pygame.display.flip()


if __name__ == "__main__":
    app = App()
    app.run()
