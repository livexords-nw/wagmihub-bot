from datetime import datetime
import time
from colorama import Fore
import requests
import random
from fake_useragent import UserAgent
import asyncio
import json
import gzip
import brotli
import zlib
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class wagmihub:
    BASE_URL = "https://api.cyberfin.xyz/api/v1/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "origin": "https://g.cyberfin.xyz",
        "referer": "https://g.cyberfin.xyz/",
        "priority": "u=1, i",
        "Content-Type": "application/json",
        "Lang": "en",
        "sec-ch-ua": '"Microsoft Edge";v="134", "Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge WebView2";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.config = self.load_config()
        self.session = self.sessions()
        self._original_requests = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        self.proxy_session = None

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Wagmi Hub Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )

    def sessions(self):
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 520]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def decode_response(self, response):
        """
        Mendekode response dari server secara umum.

        Parameter:
            response: objek requests.Response

        Mengembalikan:
            - Jika Content-Type mengandung 'application/json', maka mengembalikan objek Python (dict atau list) hasil parsing JSON.
            - Jika bukan JSON, maka mengembalikan string hasil decode.
        """
        # Ambil header
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        content_type = response.headers.get("Content-Type", "").lower()

        # Tentukan charset dari Content-Type, default ke utf-8
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()

        # Ambil data mentah
        data = response.content

        # Dekompresi jika perlu
        try:
            if content_encoding == "gzip":
                data = gzip.decompress(data)
            elif content_encoding in ["br", "brotli"]:
                data = brotli.decompress(data)
            elif content_encoding in ["deflate", "zlib"]:
                data = zlib.decompress(data)
        except Exception:
            # Jika dekompresi gagal, lanjutkan dengan data asli
            pass

        # Coba decode menggunakan charset yang didapat
        try:
            text = data.decode(charset)
        except Exception:
            # Fallback: deteksi encoding dengan chardet
            detection = chardet.detect(data)
            detected_encoding = detection.get("encoding", "utf-8")
            text = data.decode(detected_encoding, errors="replace")

        # Jika konten berupa JSON, kembalikan hasil parsing JSON
        if "application/json" in content_type:
            try:
                return json.loads(text)
            except Exception:
                # Jika parsing JSON gagal, kembalikan string hasil decode
                return text
        else:
            return text

    def login(self, index: int) -> None:
        self.log("🔐 Attempting to log in...", Fore.GREEN)
        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        self.log(f"📋 Using token: {token[:10]}... (truncated for security)", Fore.CYAN)

        # API: game/initdata (POST) menggunakan self.HEADERS
        initdata_url = f"{self.BASE_URL}game/initdata"
        payload = json.dumps({"initData": token})
        try:
            self.log("📡 Sending init data request...", Fore.CYAN)
            initdata_response = requests.post(
                initdata_url, headers=self.HEADERS, data=payload
            )
            initdata_response.raise_for_status()
            initdata = self.decode_response(initdata_response)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send init data request: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {initdata_response.text}", Fore.RED)
            except Exception:
                pass
            return
        except Exception as e:
            self.log(f"❌ Unexpected error during init data request: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {initdata_response.text}", Fore.RED)
            except Exception:
                pass
            return

        # Simpan accessToken dari response ke self.token
        try:
            access_token = initdata.get("message", {}).get("accessToken", "")
            if not access_token:
                self.log("❌ No access token received.", Fore.RED)
                return
            self.token = access_token
            self.log("✅ Init data successful! Access token saved.", Fore.GREEN)
        except Exception as e:
            self.log(f"❌ Error processing init data response: {e}", Fore.RED)
            return

        # API: game/mining/gamedata (GET)
        gamedata_url = f"{self.BASE_URL}game/mining/gamedata"
        gamedata_headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}
        try:
            self.log("📡 Sending game data request...", Fore.CYAN)
            gamedata_response = requests.get(gamedata_url, headers=gamedata_headers)
            gamedata_response.raise_for_status()
            gamedata = self.decode_response(gamedata_response)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch game data: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return
        except Exception as e:
            self.log(f"❌ Unexpected error in game data request: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return

        # Tampilin data penting dari response game data
        try:
            message = gamedata.get("message", {})
            miningData = message.get("miningData", {})
            userData = message.get("userData", {})
            squadData = message.get("squadData", {})

            self.log("🎮 Game Data:", Fore.GREEN)

            self.log("Mining Data:", Fore.GREEN)
            self.log(
                f"    - Last Claim Time: {miningData.get('lastClaimTime', 'N/A')}",
                Fore.CYAN,
            )
            self.log(
                f"    - Mining Rate: {miningData.get('miningRate', 'N/A')}", Fore.CYAN
            )
            self.log(
                f"    - Crack Time: {miningData.get('crackTime', 'N/A')}", Fore.CYAN
            )

            self.log("User Data:", Fore.GREEN)
            self.log(f"    - Balance: {userData.get('balance', 'N/A')}", Fore.CYAN)
            self.log(f"    - All Points: {userData.get('allPoints', 'N/A')}", Fore.CYAN)
            self.log(f"    - Tokens: {userData.get('tokens', 'N/A')}", Fore.CYAN)
            self.log(f"    - Country: {userData.get('country', 'N/A')}", Fore.CYAN)
            self.log(f"    - Created At: {userData.get('createdAt', 'N/A')}", Fore.CYAN)

            self.log("Squad Data:", Fore.GREEN)
            self.log(f"    - UUID: {squadData.get('uuid', 'N/A')}", Fore.CYAN)
            self.log(f"    - Title: {squadData.get('title', 'N/A')}", Fore.CYAN)
            self.log(f"    - Username: {squadData.get('username', 'N/A')}", Fore.CYAN)
            self.log(f"    - Logo URL: {squadData.get('logoUrl', 'N/A')}", Fore.CYAN)
            self.log(
                f"    - Telegram Chat ID: {squadData.get('telegramChatId', 'N/A')}",
                Fore.CYAN,
            )
        except Exception as e:
            self.log(f"❌ Error processing game data response: {e}", Fore.RED)

    def farming(self) -> None:
        self.log("🌾 Starting farming process...", Fore.GREEN)

        # Siapkan headers dengan tambahan authorization
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        # Request ke API: game/mining/gamedata
        gamedata_url = f"{self.BASE_URL}game/mining/gamedata"
        try:
            self.log("📡 Fetching game data...", Fore.CYAN)
            gamedata_response = requests.get(gamedata_url, headers=headers)
            gamedata_response.raise_for_status()
            gamedata = self.decode_response(gamedata_response)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch game data: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return
        except Exception as e:
            self.log(f"❌ Unexpected error in game data request: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return

        # Ambil miningData
        try:
            miningData = gamedata.get("message", {}).get("miningData", {})
            last_claim_time = miningData.get("lastClaimTime", None)
            mining_rate = miningData.get("miningRate", "N/A")
            crack_time = miningData.get("crackTime", None)

            self.log("🎮 Mining Data:", Fore.GREEN)
            self.log(f"    - Last Claim Time: {last_claim_time}", Fore.CYAN)
            self.log(f"    - Mining Rate: {mining_rate}", Fore.CYAN)
            self.log(f"    - Crack Time: {crack_time}", Fore.CYAN)

            if crack_time is None:
                self.log("❌ Crack time not found in the response.", Fore.RED)
                return
        except Exception as e:
            self.log(f"❌ Error processing mining data: {e}", Fore.RED)
            return

        # Bandingkan crackTime dengan waktu user (current time)
        import time

        current_time = int(time.time())
        self.log(f"⏰ Current time: {current_time}", Fore.CYAN)

        if current_time >= crack_time:
            self.log(
                "✅ Crack time has been reached. Attempting to claim mining rewards...",
                Fore.GREEN,
            )
            # Request ke API: mining/claim
            claim_url = f"{self.BASE_URL}mining/claim"
            try:
                claim_response = requests.get(claim_url, headers=headers)
                claim_response.raise_for_status()
                claim_data = self.decode_response(claim_response)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to claim mining rewards: {e}", Fore.RED)
                try:
                    self.log(f"📄 Response content: {claim_response.text}", Fore.RED)
                except Exception:
                    pass
                return
            except Exception as e:
                self.log(f"❌ Unexpected error during claim request: {e}", Fore.RED)
                try:
                    self.log(f"📄 Response content: {claim_response.text}", Fore.RED)
                except Exception:
                    pass
                return

            # Tampilkan data claim yang penting
            try:
                message = claim_data.get("message", {})
                new_miningData = message.get("miningData", {})
                userData = message.get("userData", {})

                self.log("🎉 Claim successful!", Fore.GREEN)
                self.log("New Mining Data:", Fore.GREEN)
                self.log(
                    f"    - Last Claim Time: {new_miningData.get('lastClaimTime', 'N/A')}",
                    Fore.CYAN,
                )
                self.log(
                    f"    - Mining Rate: {new_miningData.get('miningRate', 'N/A')}",
                    Fore.CYAN,
                )
                self.log(
                    f"    - Crack Time: {new_miningData.get('crackTime', 'N/A')}",
                    Fore.CYAN,
                )
                self.log("User Data:", Fore.GREEN)
                self.log(f"    - Balance: {userData.get('balance', 'N/A')}", Fore.CYAN)
                self.log(
                    f"    - All Points: {userData.get('allPoints', 'N/A')}", Fore.CYAN
                )
                self.log(f"    - Tokens: {userData.get('tokens', 'N/A')}", Fore.CYAN)
            except Exception as e:
                self.log(f"❌ Error processing claim response: {e}", Fore.RED)
        else:
            wait_time = crack_time - current_time
            self.log(
                f"⌛ Crack time not reached yet. Please wait {wait_time} seconds.",
                Fore.YELLOW,
            )

    def daily(self) -> None:
        self.log("🌞 Starting daily process...", Fore.GREEN)

        # Siapkan headers dengan tambahan authorization
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        # Request ke API: game/mining/gamedata
        gamedata_url = f"{self.BASE_URL}game/mining/gamedata"
        try:
            self.log("📡 Fetching game data for daily rewards...", Fore.CYAN)
            gamedata_response = requests.get(gamedata_url, headers=headers)
            gamedata_response.raise_for_status()
            gamedata = self.decode_response(gamedata_response)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch game data: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return
        except Exception as e:
            self.log(f"❌ Unexpected error in game data request: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {gamedata_response.text}", Fore.RED)
            except Exception:
                pass
            return

        # Ambil data daily rewards
        try:
            message = gamedata.get("message", {})
            dailyRewardsData = message.get("dailyRewardsData", {})
            dailyRewardSchema = message.get("dailyRewardSchema", [])

            current_day = dailyRewardsData.get("currentDay", "N/A")
            is_claimed = dailyRewardsData.get("isClaimed", None)
            is_show_daily_reward = dailyRewardsData.get("isShowDailyReward", "N/A")

            self.log("🌞 Daily Rewards Data:", Fore.GREEN)
            self.log(f"    - Current Day: {current_day}", Fore.CYAN)
            self.log(f"    - Is Claimed: {is_claimed}", Fore.CYAN)
            self.log(f"    - Is Show Daily Reward: {is_show_daily_reward}", Fore.CYAN)

            self.log("🌞 Daily Reward Schema:", Fore.GREEN)
            for reward in dailyRewardSchema:
                day = reward.get("day", "N/A")
                reward_amount = reward.get("reward", "N/A")
                self.log(f"    - Day {day}: Reward {reward_amount}", Fore.CYAN)

            # Jika daily reward belum diklaim, maka klaim
            if is_claimed is False:
                self.log(
                    "✅ Daily reward not yet claimed. Attempting to claim...",
                    Fore.GREEN,
                )
                claim_daily_url = f"{self.BASE_URL}mining/claim/daily"
                try:
                    claim_daily_response = requests.post(
                        claim_daily_url, headers=headers
                    )
                    claim_daily_response.raise_for_status()
                    claim_daily_data = self.decode_response(claim_daily_response)
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Failed to claim daily reward: {e}", Fore.RED)
                    try:
                        self.log(
                            f"📄 Response content: {claim_daily_response.text}",
                            Fore.RED,
                        )
                    except Exception:
                        pass
                    return
                except Exception as e:
                    self.log(
                        f"❌ Unexpected error during daily claim request: {e}", Fore.RED
                    )
                    try:
                        self.log(
                            f"📄 Response content: {claim_daily_response.text}",
                            Fore.RED,
                        )
                    except Exception:
                        pass
                    return

                try:
                    claim_message = claim_daily_data.get("message", {})
                    day_claimed = claim_message.get("day", "N/A")
                    reward_claimed = claim_message.get("reward", "N/A")
                    self.log("🎉 Daily reward claimed!", Fore.GREEN)
                    self.log(f"    - Day: {day_claimed}", Fore.CYAN)
                    self.log(f"    - Reward: {reward_claimed}", Fore.CYAN)
                except Exception as e:
                    self.log(f"❌ Error processing daily claim response: {e}", Fore.RED)
            else:
                self.log("ℹ️ Daily reward has already been claimed today.", Fore.YELLOW)
        except Exception as e:
            self.log(f"❌ Error processing daily rewards data: {e}", Fore.RED)

    def task(self) -> None:
        self.log("🔔 Starting task process...", Fore.GREEN)
        # Siapkan headers dengan tambahan authorization
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        # Request ke API: gametask/all (GET)
        gametask_all_url = f"{self.BASE_URL}gametask/all"
        try:
            self.log("📡 Fetching game tasks...", Fore.CYAN)
            gametask_all_response = requests.get(gametask_all_url, headers=headers)
            gametask_all_response.raise_for_status()
            gametask_all_data = self.decode_response(gametask_all_response)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch game tasks: {e}", Fore.RED)
            return
        except Exception as e:
            self.log(f"❌ Unexpected error in game tasks request: {e}", Fore.RED)
            return

        try:
            tasks = gametask_all_data.get("message", [])
            if not tasks:
                self.log("ℹ️ No tasks available.", Fore.YELLOW)
            else:
                self.log("🎮 Available tasks:", Fore.GREEN)
                for task in tasks:
                    # Proses hanya task yang belum selesai dan masih aktif
                    if (
                        task.get("isCompleted") is False
                        and task.get("isActive") is True
                    ):
                        uuid = task.get("uuid")
                        title = task.get("title", "N/A")
                        self.log(f"    - Task: {title} (UUID: {uuid})", Fore.CYAN)

                        # Claim dan complete task dengan GET ke gametask/complete/{uuid}
                        complete_url = f"{self.BASE_URL}gametask/complete/{uuid}"
                        try:
                            self.log(f"📡 Completing task '{title}'...", Fore.CYAN)
                            complete_response = requests.get(
                                complete_url, headers=headers
                            )
                            complete_response.raise_for_status()
                            complete_data = self.decode_response(complete_response)
                            completed_task = complete_data.get("message", {})
                            if completed_task.get("isCompleted"):
                                self.log(f"✅ Task '{title}' completed.", Fore.GREEN)
                            else:
                                self.log(
                                    f"⚠️ Task '{title}' did not complete as expected.",
                                    Fore.YELLOW,
                                )
                        except requests.exceptions.RequestException as e:
                            self.log(
                                f"❌ Failed to complete task '{title}': {e}", Fore.RED
                            )
                        except Exception as e:
                            self.log(
                                f"❌ Unexpected error while completing task '{title}': {e}",
                                Fore.RED,
                            )
                    else:
                        self.log(
                            f"ℹ️ Skipping task '{task.get('title', 'N/A')}' (completed or inactive).",
                            Fore.YELLOW,
                        )
        except Exception as e:
            self.log(f"❌ Error processing game tasks data: {e}", Fore.RED)

    def game(self) -> None:
        self.log("🎲 Starting game process...", Fore.GREEN)
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}
        bet_amount = 30000
        prediction = random.choice(["RIGHT", "LEFT"])

        # Fungsi untuk memasang taruhan dan mengecek statusnya
        def place_and_check_bet():
            place_bet_url = f"{self.BASE_URL}binary/place-bet"
            payload = json.dumps(
                {
                    "binaryTokenId": "12",
                    "amount": str(bet_amount),
                    "prediction": prediction,
                    "timeLength": 15,
                }
            )
            try:
                self.log(f"📡 Placing bet with prediction {prediction}...", Fore.CYAN)
                place_response = requests.post(
                    place_bet_url, headers=headers, data=payload
                )
                place_response.raise_for_status()
                place_data = self.decode_response(place_response)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to place bet: {e}", Fore.RED)
                return None
            except Exception as e:
                self.log(f"❌ Unexpected error placing bet: {e}", Fore.RED)
                return None

            bet_id = place_data.get("message", {}).get("id")
            if not bet_id:
                self.log("❌ Bet ID not found in response.", Fore.RED)
                return None

            self.log(
                f"✅ Bet placed successfully with id {bet_id}. Waiting 15 seconds...",
                Fore.GREEN,
            )
            time.sleep(15)

            check_bet_url = f"{self.BASE_URL}binary/check-bet/{bet_id}"
            try:
                self.log(f"📡 Checking bet status for id {bet_id}...", Fore.CYAN)
                check_response = requests.get(check_bet_url, headers=headers)
                check_response.raise_for_status()
                check_data = self.decode_response(check_response)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to check bet {bet_id}: {e}", Fore.RED)
                return None
            except Exception as e:
                self.log(f"❌ Unexpected error checking bet {bet_id}: {e}", Fore.RED)
                return None

            bet_status = (
                check_data.get("message", {}).get("bet", {}).get("status", "N/A")
            )
            self.log(f"🎲 Bet {bet_id} status: {bet_status}", Fore.GREEN)
            return bet_id

        # Main loop: terus periksa data game hingga tiket atau saldo tidak mencukupi
        while True:
            # Request game data
            gamedata_url = f"{self.BASE_URL}game/mining/gamedata"
            try:
                self.log("📡 Fetching game data...", Fore.CYAN)
                gamedata_response = requests.get(gamedata_url, headers=headers)
                gamedata_response.raise_for_status()
                gamedata = self.decode_response(gamedata_response)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to fetch game data: {e}", Fore.RED)
                break
            except Exception as e:
                self.log(f"❌ Unexpected error fetching game data: {e}", Fore.RED)
                break

            message = gamedata.get("message", {})
            ticket_count = message.get("ticketCount", 0)
            balance_str = message["userData"].get("balance", "0")
            try:
                balance = int(balance_str)
            except Exception:
                balance = 0

            self.log(f"🎟 Ticket Count: {ticket_count}", Fore.CYAN)
            self.log(f"💰 Balance: {balance}", Fore.CYAN)

            # Validasi: pastikan tiket tersedia dan saldo mencukupi
            if ticket_count <= 0:
                self.log("ℹ️ No tickets available, ending game process.", Fore.YELLOW)
                break
            if balance < bet_amount:
                self.log("ℹ️ Insufficient balance to place a bet.", Fore.YELLOW)
                break

            # Lakukan taruhan satu per satu
            self.log("🚀 Placing a single bet...", Fore.GREEN)
            place_and_check_bet()

            # Setelah taruhan, tunggu beberapa saat dan periksa ulang data game
            self.log("🔄 Rechecking game data after bet...", Fore.CYAN)
            time.sleep(3)

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

    def override_requests(self):
        import random

        """Override requests functions globally when proxy is enabled."""
        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete
        else:
            self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
            # Restore original functions if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]


async def process_account(account, original_index, account_label, wagmi, config):
    # Menampilkan informasi akun
    display_account = account[:10] + "..." if len(account) > 10 else account
    wagmi.log(f"👤 Processing {account_label}: {display_account}", Fore.YELLOW)

    # Override proxy jika diaktifkan
    if config.get("proxy", False):
        wagmi.override_requests()
    else:
        wagmi.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

    # Login (fungsi blocking, dijalankan di thread terpisah) dengan menggunakan index asli (integer)
    await asyncio.to_thread(wagmi.login, original_index)

    wagmi.log("🛠️ Starting task execution...", Fore.CYAN)
    tasks_config = {
        "daily": "Daily Reward Check & Claim 🎁",
        "task": "Automatically solving tasks 🤖",
        "farming": "Automatic farming for abundant harvest 🌾",
        "game": "Play exciting game and earn points 🎮",
    }

    for task_key, task_name in tasks_config.items():
        task_status = config.get(task_key, False)
        color = Fore.YELLOW if task_status else Fore.RED
        wagmi.log(
            f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
            color,
        )
        if task_status:
            wagmi.log(f"🔄 Executing {task_name}...", Fore.CYAN)
            await asyncio.to_thread(getattr(wagmi, task_key))

    delay_switch = config.get("delay_account_switch", 10)
    wagmi.log(
        f"➡️ Finished processing {account_label}. Waiting {Fore.WHITE}{delay_switch}{Fore.CYAN} seconds before next account.",
        Fore.CYAN,
    )
    await asyncio.sleep(delay_switch)


async def worker(worker_id, wagmi, config, queue):
    """
    Setiap worker akan mengambil satu akun dari antrian dan memprosesnya secara berurutan.
    Worker tidak akan mengambil akun baru sebelum akun sebelumnya selesai diproses.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, wagmi, config)
        queue.task_done()
    wagmi.log(
        f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN
    )


async def main():
    wagmi = wagmihub()  # Inisialisasi instance class wagmihub Anda
    config = wagmi.load_config()
    all_accounts = wagmi.query_list
    num_threads = config.get("thread", 1)  # Jumlah worker sesuai konfigurasi

    if config.get("proxy", False):
        proxies = wagmi.load_proxies()

    wagmi.log(
        "🎉 [LIVEXORDS] === Welcome to Wagmi Hub Automation === [LIVEXORDS]",
        Fore.YELLOW,
    )
    wagmi.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)

    while True:
        # Buat queue baru dan masukkan semua akun (dengan index asli)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))

        # Buat task worker sesuai dengan jumlah thread yang diinginkan
        workers = [
            asyncio.create_task(worker(i + 1, wagmi, config, queue))
            for i in range(num_threads)
        ]

        # Tunggu hingga semua akun di queue telah diproses
        await queue.join()

        # Opsional: batalkan task worker (agar tidak terjadi tumpang tindih)
        for w in workers:
            w.cancel()

        wagmi.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        wagmi.log(
            f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.",
            Fore.CYAN,
        )
        await asyncio.sleep(delay_loop)


if __name__ == "__main__":
    asyncio.run(main())
