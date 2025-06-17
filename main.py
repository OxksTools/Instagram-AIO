import os
import threading
import time
import requests
from colorama import Fore, init
from itertools import cycle
from pystyle import Write, Colors

init(autoreset=True)


class CookieManager:
    @staticmethod
    def load_cookies(file_path='data/cookies.txt'):
        try:
            with open(file_path, 'r') as f:
                cookies = [line.strip() for line in f if line.strip()]
            return cycle(cookies)
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Cookie file not found at '{file_path}'")
            exit()


class InstagramAIO:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = CookieManager.load_cookies()

    def get_user_id(self, username):
        try:
            headers = {
                'user-agent': 'Mozilla/5.0',
                'x-ig-app-id': '936619743392459'
            }
            response = self.session.get(
                'https://i.instagram.com/api/v1/users/web_profile_info/',
                headers=headers,
                params={'username': username}
            )
            return response.json()['data']['user']['id']
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to fetch user ID: {e}")

    def get_post_id(self, shortcode):
        try:
            headers = {'user-agent': 'Mozilla/5.0'}
            url = f'https://www.instagram.com/p/{shortcode}/'
            html = self.session.get(url, headers=headers).text
            return html.split('postPage_')[1].split('"')[0]
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to fetch post ID: {e}")

    def perform_action(self, url, headers, data=None):
        try:
            cookie = next(self.cookies)
            headers['cookie'] = f'sessionid={cookie}'
            r = self.session.post(url, headers=headers, data=data)
            return r.status_code == 200
        except Exception as e:
            print(f"{Fore.RED}[!] Request failed: {e}")
            return False

    def follow(self, user_id):
        headers = {'user-agent': 'Mozilla/5.0', 'x-csrftoken': 'csrftoken_placeholder'}
        success = self.perform_action(f'https://www.instagram.com/web/friendships/{user_id}/follow/', headers)
        print(f"{Fore.GREEN}[+] Followed" if success else f"{Fore.RED}[x] Failed")

    def unfollow(self, user_id):
        headers = {'user-agent': 'Mozilla/5.0', 'x-csrftoken': 'csrftoken_placeholder'}
        success = self.perform_action(f'https://www.instagram.com/web/friendships/{user_id}/unfollow/', headers)
        print(f"{Fore.GREEN}[+] Unfollowed" if success else f"{Fore.RED}[x] Failed")

    def like(self, post_id):
        headers = {'user-agent': 'Mozilla/5.0', 'x-csrftoken': 'csrftoken_placeholder'}
        success = self.perform_action(f'https://www.instagram.com/web/likes/{post_id}/like/', headers)
        print(f"{Fore.GREEN}[+] Liked" if success else f"{Fore.RED}[x] Failed")

    def comment(self, post_id, text):
        headers = {'user-agent': 'Mozilla/5.0', 'x-csrftoken': 'csrftoken_placeholder'}
        data = {'comment_text': text}
        success = self.perform_action(f'https://www.instagram.com/web/comments/{post_id}/add/', headers, data)
        print(f"{Fore.GREEN}[+] Commented" if success else f"{Fore.RED}[x] Failed")


class InstagramToolMenu:
    def __init__(self):
        self.ig = InstagramAIO()

    def display_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('title Instagram AIO | by github.com/OxksTools' if os.name == 'nt' else '')
        Write.Print("""
 ██╗███╗ ██╗ ██████╗████████╗  █████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗
 ██║████╗ ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
 ██║██╔██╗██║╚█████╗    ██║   ███████║██║  ██╗ ██████╔╝███████║██╔████╔██║
 ██║██║╚████║ ╚═══██╗   ██║   ██╔══██║██║  ╚██╗██╔══██╗██╔══██║██║╚██╔╝██║
 ██║██║ ╚███║██████╔╝   ██║   ██║  ██║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
 ╚═╝╚═╝ ╚══╝╚═════╝     ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
        """, Colors.purple_to_blue, interval=0.001)

    def menu(self):
        self.display_banner()
        print(f"{Fore.CYAN}[1]{Fore.RESET} Follow    {Fore.CYAN}[2]{Fore.RESET} Unfollow")
        print(f"{Fore.CYAN}[3]{Fore.RESET} Like      {Fore.CYAN}[4]{Fore.RESET} Comment\n")
        choice = input(f"{Fore.GREEN}[?] Choice > {Fore.WHITE}")

        if choice == '1':
            self.mass_action('follow')
        elif choice == '2':
            self.mass_action('unfollow')
        elif choice == '3':
            self.mass_action('like')
        elif choice == '4':
            self.mass_action('comment')
        else:
            print(f"{Fore.RED}[!] Invalid option")

    def mass_action(self, action):
        if action in ['follow', 'unfollow']:
            username = input(f"{Fore.CYAN}[?] Username > {Fore.WHITE}")
            count = int(input(f"{Fore.CYAN}[?] Threads > {Fore.WHITE}"))
            user_id = self.ig.get_user_id(username)
            for _ in range(count):
                threading.Thread(target=getattr(self.ig, action), args=(user_id,)).start()

        elif action == 'like':
            post = input(f"{Fore.CYAN}[?] Post Shortcode > {Fore.WHITE}")
            count = int(input(f"{Fore.CYAN}[?] Threads > {Fore.WHITE}"))
            post_id = self.ig.get_post_id(post)
            for _ in range(count):
                threading.Thread(target=self.ig.like, args=(post_id,)).start()

        elif action == 'comment':
            post = input(f"{Fore.CYAN}[?] Post Shortcode > {Fore.WHITE}")
            message = input(f"{Fore.CYAN}[?] Comment Text > {Fore.WHITE}")
            count = int(input(f"{Fore.CYAN}[?] Threads > {Fore.WHITE}"))
            post_id = self.ig.get_post_id(post)
            for _ in range(count):
                threading.Thread(target=self.ig.comment, args=(post_id, message)).start()


if __name__ == "__main__":
    InstagramToolMenu().menu()
