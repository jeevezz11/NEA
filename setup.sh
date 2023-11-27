#!/bin/zsh

# Version 0.8 for Linux #

output_location="&>/dev/null"
flag="--quiet"
curl_flag="-s"

while getopts ":nv" opt; do
    case $opt in
        n)
            nosleep="true"  # This means that all the waits will be ignored throughout the script mainly for testing efficiency
            ;;
        v)
            output_location="&>/dev/stdout"  # Verbose option for debugging
            flag="--verbose"
            curl_flag="-v"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2  # Catch invalid options
            exit 1  # Don't run code with an invalid flag
            ;;
    esac
done

function wait() {

    if [ -z "$nosleep" ]; then # if no sleep isnt set to true then it will sleep for 1 second throughout the script so the user can process what is happening as it happens 
        sleep 1
    fi

}

function valid_password() {
    
    echo -n "Enter new admin password: "
    read -s first_password
    echo ""

    echo -n "Confirm password: "
    read -s second_password
    echo ""

    wait

    if [ "$first_password" = "$second_password" ]; then # makes sure the passwords match
        password="$first_password"
        hashed_password=$(echo -n "$password" | sha256sum | cut -d ' ' -f 1)
        wait
        echo -n "Enter admin alias: "
        read alias
    else
        echo "Passwords don't match, Please try again"
        wait
        valid_password # recursion until we get a matching password
    fi
}

function install_program() {

    local repo="https://raw.githubusercontent.com/jeevezz11/NEA/main"
    local file_name="$1"

    if ! test -e "$file_name"; then
        echo "Installing $file_name..."
        curl -LO $curl_flag "$repo/$file_name"
        echo "$file_name has been installed"
    else
        echo "$file_name found"
    fi  

wait

}

function pacman_installer() {

local program="$1"
if ! command -v "$program" &>/dev/null; then # checks if the command can be ran but -v doesnt actually run it and it sends any output to /dev/null
    echo "$program is not installed. Installing $program..." # so it essentially lost as it isn't needed
    sudo pacman $flag -S --noconfirm --needed $program # --noconfirm is used to skip any questions the system might ask you and just selects the default option to speed things up
    echo "$program has been installed"
else
    echo "$program is already installed"
fi

wait

}

function aur_installer() {

local program="$1"
if ! yay -Qq $program &>/dev/null; then # same again
    echo "Installing $program..."
    yay -S $flag --noconfirm --needed $program
    echo "$program has been installed"
else
    echo "$program is already installed"
fi

wait

}

pacman_installer python
pacman_installer zenity
pacman_installer curl

aur_installer python-tkcalendar
aur_installer sqlite3

install_program main.py
install_program gui.py
install_program orderPad.py

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # sets the variable to the same directory the script is running from 

# Config.ini file handling
ini_files=( $(find "$script_dir" -name "*.ini") ) # looks for files with the extension .ini in the script directory

if [ ${#ini_files[@]} -eq 0 ]; then # if theres no ini files
    echo "No config.ini file found"
    wait
    echo -n "Do you want to download config.ini from GitHub? (Y/n): "
    read download_config
    download_config=${download_config:-Y}
    if [ "$download_config" = "Y" ] || [ "$download_config" = "y" ]; then
        github_raw_url="https://raw.githubusercontent.com/jeevezz11/NEA/main/config.ini" # downloads it from my github
        curl -LO $curl_flag "$script_dir/config.ini" "$github_raw_url"
        echo "Downloaded config.ini from GitHub"
        config_file_found="true"
    fi
else
    for ini_file in "${ini_files[@]}"; do
        if [ "$ini_file" != "$script_dir/config.ini" ]; then # if it finds a config file that isn't called config.ini it asks wether this is the intended file
            echo "Found .ini file at: $ini_file"
            echo -n "Is this your config .ini file? (Y/n): "
            wait    
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                mv "$ini_file" "$script_dir/config.ini"
                echo "Renamed $ini_file to config.ini" # renames it appropriately to allow the code to function correctly
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
    if ! grep -q "$script_dir" "$config_file"; then # checks if the script directory is set as the program folder in the config file 
        sed -i "s|programFolder: .*|programFolder: $script_dir|" "$config_file" # if it isn't it sets it so it is
        echo "Program Folder Path in config.ini file changed to $script_dir"
    else
        echo "Program folder found"
    fi

    wait

    data_line=$(grep "^data:" config.ini) 
    data_directory=$(echo "$data_line" | sed 's/^data:[[:space:]]*//') # whatever directory is currently in the data folder is added to a variable to check if it's valid

    if grep -q "^data:.*<user>" "$config_file" || if ! test -d "$data_directory"; then
        data_directory=$(zenity --file-selection --directory --title="Select your 'data' folder" 2>/dev/null) # if it isn't valid or this is a fresh install and its set to the default
        echo "Data Folder Path in config.ini file changed to $data_directory"                                 # this allows you to set your data directory manually
        sed -i "s|^data: .*|data: $data_directory|" "$config_file"
    else
        echo "Data folder found"
    fi

fi

wait

# Database file handling
database_files=$(find "$data_directory" -type f -name "*.db") # finds .db files and does basically the same as it did with the .ini files 

if [ ${#database_files[@]} -eq 0 ]; then
    echo "No database.db file found in the script's directory"
    echo -n "Do you want to download database.db from GitHub? (Y/n): "
    wait
    read download_db
    download_db=${download_db:-Y}
    if [ "$download_db" = "Y" ] || [ "$download_db" = "y" ]; then
        if command -v curl &>/dev/null; then
            github_raw_url="https://raw.githubusercontent.com/jeevezz11/NEA/main/database.db"
            curl -LO $curl_flag "$data_directory/database.db" "$github_raw_url"
            echo "Downloaded database.db from GitHub"
        fi
        wait

    fi
else
    for database_file in "${database_files[@]}"; do
        if [ "$database_file" != "$data_directory/database.db" ]; then
            echo "Found database.db file at: $database_file"
            echo -n "Is this your database file? (Y/n): "
            wait
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                mv "$database_file" "$data_directory/database.db"
                echo "Renamed $database_file to database.db"
            fi
        else
            echo "database.db found"
            wait
        fi
    done
fi

database_path=("$data_directory/database.db")

results=$(sqlite3 "$database_path" "SELECT * FROM passwords;") # checks if an admin password has been set

if [ -z "$results" ]; then # if not
    echo "No admin password found"
    wait
    valid_password # run the password setter and validator
    sqlite3 "$database_path" "INSERT INTO passwords (admin_alias, hashed_password) VALUES ('$alias', '$hashed_password');" # put it into the database
fi

# Run the Python script if config.ini and database.db are present
if [ -e "$script_dir/config.ini" ] && [ -e "$data_directory/database.db" ]; then
    echo "Running without issues"
    python3 "$script_dir/gui.py" >/dev/null 2>&1
else
    echo "Necessary dependencies not found"
    wait    
    echo "Failed to run program"
    exit 127
fi
