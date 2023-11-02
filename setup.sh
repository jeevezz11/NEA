#!/bin/zsh

# Version 0.8 for Linux #

while getopts ":n" opt; do #checks for an -n flag after the command for example "./setup.sh -n"
    case $opt in
        n)
            nosleep="true" #this means that all the waits will be ignored throughout the script mainly for testing efficiency
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2 #catch invalid options
            exit 1 #dont run code with invalid flag
            ;;
    esac
done

function wait() {

    if [ -z "$nosleep" ]; then # -z checks if the argument has nothing in it so if it wasn't set to true but the 
        sleep 1
    fi

}

shift $((OPTIND-1))

function valid_password() {
    
    echo -n "Enter new admin password: "
    read -s first_password
    echo ""

    echo -n "Confirm password: "
    read -s second_password
    echo ""

    wait

    if [ "$first_password" = "$second_password" ]; then
        password="$first_password"
        hashed_password=$(echo -n "$password" | sha256sum | cut -d ' ' -f 1)
        wait
        echo -n "Enter admin alias: "
        read alias
    else
        echo "Passwords don't match, Please try again"
        wait
        valid_password
    fi
}

# Check for Python
if ! command -v python3 &>/dev/null; then
    echo "Python is not installed. Installing Python..."
    sudo pacman -S python3
    echo "Python has been installed"
else
    echo "Python is already installed"
fi

wait

# Check and install python-tkcalendar
if ! yay -Qq python-tkcalendar &>/dev/null; then
    echo "Installing python-tkcalendar..."
    yay -S --noconfirm python-tkcalendar
    echo "python-tkcalendar has been installed"
else
    echo "python-tkcalendar is already installed"
fi

wait

# Check and install sqlite3
if ! yay -Qq sqlite3 &>/dev/null; then
    echo "Installing sqlite3..."
    yay -S --noconfirm sqlite3
    echo "sqlite3 has been installed"
else
    echo "sqlite3 is already installed"
fi
wait

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$script_dir"

# Config.ini file handling
ini_files=( $(find "$script_dir" -name "*.ini") )

if [ ${#ini_files[@]} -eq 0 ]; then
    echo "No config.ini file found"
    wait
    echo -n "Do you want to download config.ini from GitHub? (Y/n): "
    read download_config
    download_config=${download_config:-Y}
    if [ "$download_config" = "Y" ] || [ "$download_config" = "y" ]; then
        github_raw_url="https://raw.githubusercontent.com/jeevezz11/NEA/main/config.ini"
        curl -o "$script_dir/config.ini" "$github_raw_url"
        echo "Downloaded config.ini from GitHub"
        config_file_found="true"
    fi
else
    for ini_file in "${ini_files[@]}"; do
        if [ "$ini_file" != "$script_dir/config.ini" ]; then
            echo "Found .ini file at: $ini_file"
            echo -n "Is this your config .ini file? (Y/n): "
            wait    
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                mv "$ini_file" "$script_dir/config.ini"
                echo "Renamed $ini_file to config.ini"            
                config_file_found="true"
            fi
        else
            echo "config.ini found"
            config_file_found="true"
        fi
    done
fi

wait

if [ "$config_file_found" = "true" ]; then
    config_file="$script_dir/config.ini"
    config_script_dir="$script_dir/"
    if ! grep -q "$config_script_dir" "$config_file"; then
        sed -i "s|programFolder: .*|programFolder: $config_script_dir|" "$config_file"
        echo "Program Folder Path in config.ini file changed to $config_script_dir"
    fi

    selected_folder=$(zenity --file-selection --directory --title="Select your 'data' folder")
    sed -i "s|data: .*|data: $selected_folder/|" "$config_file"
    echo "Data Folder Path in config.ini file changed to $selected_folder"
fi

# Database file handling
database_files=$(find "$selected_folder" -type f -name "*.db")

if [ ${#database_files[@]} -eq 0 ]; then
    echo "No database.db file found in the script's directory"
    echo -n "Do you want to download database.db from GitHub? (Y/n): "
    wait
    read download_db
    download_db=${download_db:-Y}
    if [ "$download_db" = "Y" ] || [ "$download_db" = "y" ]; then
        if command -v curl &>/dev/null; then
            github_raw_url="https://raw.githubusercontent.com/jeevezz11/NEA/main/database.db"
            curl -o "$selected_folder/database.db" "$github_raw_url"
            echo "Downloaded database.db from GitHub"
        else
            echo "curl is not available. You need to install curl to download the database." #change this so it installs curl instead
        fi
        wait

    fi
else
    for database_file in "${database_files[@]}"; do
        if [ "$database_file" != "$selected_folder/database.db" ]; then
            echo "Found database.db file at: $database_file"
            echo -n "Is this your database file? (Y/n): "
            wait
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                mv "$database_file" "$selected_folder/database.db"
                echo "Renamed $database_file to database.db"
            fi
        else
            echo "database.db found"
            wait
        fi
    done
fi

database_path=("$selected_folder/database.db")

results=$(sqlite3 "$database_path" "SELECT * FROM passwords;")

if [ -z "$results" ]; then
    echo "No admin password found"
    wait
    valid_password
    sqlite3 "$database_path" "INSERT INTO passwords (admin_alias, hashed_password) VALUES ('$alias', '$hashed_password');"
fi

# Run the Python script if config.ini and database.db are present
if [ -e "$script_dir/config.ini" ] && [ -e "$selected_folder/database.db" ]; then
    echo "Running without issues"
    python "$script_dir/gui.py" >/dev/null 2>&1
else
    echo "Necessary dependencies not found"
    wait    
    echo "Failed to run program"
fi
