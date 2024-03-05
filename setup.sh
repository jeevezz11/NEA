#!/bin/zsh
# Version 0.10 for Linux #

# Set default values
debug_config=false 
nosleep=""
change_password=false
reset_script=false

while getopts ":n-:" opt; do # evaluate the flags that the setup script is ran with 
    case $opt in 
        n) # if it is ran with the -n flag
            nosleep=true # run in no sleep mode (used for testing)
            ;;
        -)
            case "${OPTARG}" in 
                changepassword) # if it is ran with --changepassword
                    change_password=true 
                    ;;
                debug) # if it is ran with --debug
                    debug_config=true
                    ;;
                reset) # if it is ran with --reset 
                    echo -n "Are you sure you want to reset the program to the latest version on GitHub (This is irreversible)? (y/N): "
                    read confirmation

                    confirmation=${confirmation:-n} # default the value to no for safety

                    case "$confirmation" in
                        n|N) # if they say no
                            echo -n "Exiting" # exit the script
        
                        for i in {1..3}; do
                            sleep 0.5
                            echo -n "." # add elipses (aesthetic)
                        done

                        echo    # move to the next line after the loop (aesthetic)
                        exit 0 # exit the script
                        ;;

                        y|Y) # if they explicitly say yes then set these arguments to true
                            debug_config=true
                            reset_script=true
                            ;;
                        *)
                            echo "Invalid option: --${OPTARG}" >&2 # if they enter an invalid option exit the script
                            exit 1
                            ;;
                    esac
                    ;;
                \?)
                    echo "Invalid option: --${OPTARG}" >&2 # if an invalid flag is ran with the script exit
                    exit 1
                    ;;
            esac
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2 # if an invalid short form flag is ran with the script exit
            exit 1
            ;;
    esac
done

# if the script is ran without the -n flag then the wait function will cause the script to slow down at various points in the script to allow the user to process the information

wait() { 
    if [ -z "$nosleep" ]; then 
        sleep 1
    fi
}


valid_password() { # a function used to create a valid admin password and add it to the database 
    attempt=1
    while [ "$attempt" -le 3 ]; do # 3 attempts to get the password to match
        remaining=$((4-attempt)) # calculate how many attempts the user has left
        echo -n "Enter new admin password ('$remaining attempts remaining'): " 
        read -s first_password # enter and save the first password entry
        echo ""

        echo -n "Confirm password: " 
        read -s second_password # enter and save the second password entry
        echo ""
        wait

        if [ "$first_password" = "$second_password" ]; then # if the passwords match
            password="$first_password"
            hashed_password=$(echo -n "$password" | sha256sum | cut -d ' ' -f 1) # hash the password using the SHA256 hashing algorithm 
            
            echo "Password set successfully!"
            
            echo -n "Enter admin alias: "
            read alias # set an admin alias to store in the table 

            return
        else
            echo "Passwords don't match. Please try again."
            ((attempt++)) # increment attempt
        fi
    done

    echo "Maximum attempts reached. Exiting."
    exit 1 # if the user doesnt enter a matching password in 3 attempts, exit
}

install_program() { # a function used to isntall a program script from github
    local repo="https://raw.githubusercontent.com/jeevezz11/NEA/main"
    local file_name="$1" # take the first arguments after the function call as the file name to download

    if [ ! -e "$file_name" ]; then # if the file doesn't exist in the current directory
        echo "Installing $file_name..."

        if [ $file_name = "database.db" ]; then
            curl -LO "$repo/$file_name" -o "$data_directory" # install database to data directory instead of script directory 
        else
            curl -LO "$repo/$file_name" # install the file from the github using curl
        fi
        
        echo "$file_name has been installed" 
    else
        echo "$file_name found" # if the file exists there is no need to install it 
    fi  

    wait
}

pacman_install() { # a function to install packages using pacman if they're not already installed
    local program="$1" # take the first argument as the program name
    if ! command -v "$program" &>/dev/null; then # if the package isn't available
        echo "$program is not installed. Installing $program..."
        sudo pacman -S --noconfirm --needed $program # install it using pacman (--noconfirm will automatically select the default option for each situation and --needed will only download the files you need instead of downloading everything including redownloading files that exist on the device)
        echo "$program has been installed"
    else
        echo "$program is already installed"
    fi

    wait
}

aur_install() { # a function that operates identially to pacman_install but installs packages using the arch user repository
    local program="$1"
    if ! yay -Qq $program &>/dev/null; then # if the program doesn't exist 
        echo "Installing $program..."
        yay -S --noconfirm --needed $program # download it 
        echo "$program has been installed"
    else
        echo "$program is already installed"
    fi

    wait
}

delete_file() { # a function to delete files if running the script in reset mode
    local file_path="$1"

    echo $file_path

    if [ -e "$file_path" ]; then # if the file exists        
        rm "$file_path" # remove it
        wait
        echo "$file_path deleted successfully."
    fi
}

# Declare a global variable for the data directory path
data_directory=""

if [ "$debug_config" = true ]; then # if the script is being ran with --debug or --reset then all the values in the config.ini settings will be reset to nothing so that the program allows you to manually set them again
    sed -i 's/^data = .*/data = /' "config.ini" 
    sed -i 's/^public_key_path = .*/public_key_path = /' "config.ini"
    sed -i 's/^private_key_path = .*/private_key_path = /' "config.ini"
    sed -i 's/^elevated_privellege = .*/elevated_privellege = False/' "config.ini"
fi

update_config_directory() { # a function to update values in the config file
    local config_key="$1" # the key of what is being updated will be the first argument of the function call
    
    config_line=$(grep "^$config_key = " config.ini)
    config_value=$(echo "$config_line" | sed "s/^$config_key = [[:space:]]*//")

    if [ "$config_key" = "data" ]; then
        if grep -q "^$config_key = .*<user>" config.ini || [ ! -d "$config_value" ]; then # if the value for data contains "<user>" which is what the default value is for the github version of the file or if the directory associated with data doesn't exist (which if it has been reset to nothing means that it will be ran as "" is not a valid directory)
            data_directory=$(zenity --file-selection --directory --title="Select your '$config_key' folder" 2>/dev/null) # the new data directory is going to be whatever directory you select using zenity which is a folder and file selection tool
            echo "$config_key Folder Path in config.ini file changed to $data_directory" # alert the user to the exact directory that the value has been changed to 
            sed -i "s|^$config_key = .*|$config_key = $data_directory|" config.ini # update the value in the file
        else
            echo "$config_key folder found" # if the directory is valid then do nothing 
        fi
    else
        existing_file_path=$(grep "^$config_key = " config.ini | sed 's/^$config_key = [[:space:]]*//')

        if [[ "$existing_file_path" != *.pem ]]; then # if you're changing an encryption key's directory check that the value is a pem file
            new_file=$(zenity --file-selection --title="Select your '$config_key' file" --file-filter='*.pem' 2>/dev/null) # if it isn't use zenity to pick a .pem file to set this key to
            sed -i "s|^$config_key = .*|$config_key = $new_file|" config.ini # update the config file          
            echo "$config_key File Path in config.ini file changed to $new_file"
        else
            echo "$config_key found"
        fi
    fi

    wait
}

if [ "$change_password" = true ]; then # if the script is being ran with --changepassword
    attempt=1

    data_directory=$(sed -n 's/^data = [[:space:]]*//p' "config.ini") # determine what the data directory is using the config file
    database_path="${data_directory}/database.db" # meaning this is the database directory 
    search_query="SELECT \`hashed_password\` FROM \`passwords\`" # using this SQL we can retrieve the current password
    current_password=$(sqlite3 "${database_path}" "${search_query}") # execute the SQL query

    echo -n "Enter your password: " # enter your current password 
    read -s entered_password
    echo

    entered_password_hashed=$(echo -n "${entered_password}" | sha256sum | awk '{print $1}') # hash the entry

    if [ "${entered_password_hashed}" != "${current_password}" ]; then
        echo "Incorrect password. Exiting." # if the passwords don't match 
        exit 1 # exit
    fi

    if [ -e "$database_path" ]; then # if the database path is a real path
        valid_password # run the valid password function to set a new password
        sqlite3 "$database_path" "DELETE FROM passwords;" # delete the current password in the database using SQL
        sqlite3 "$database_path" "INSERT INTO passwords (admin_alias, hashed_password) VALUES ('$alias', '$hashed_password');" # add the new hashed password and alias
        echo "Password changed successfully. Exiting."
        exit 0 # exit without any errors for --changepassword
    else
        echo "Database not found"
        wait
        echo "Run ./setup.sh to set up the program and try again"
        exit 1  
    fi
fi

# install the following packages if they don't ecist 

pacman_install python 
pacman_install zenity 
pacman_install curl 

# install the python libraries if they don't exist on the system

aur_install python-tkcalendar 
aur_install sqlite3
aur_install python-cryptography

# Delete files only if running the script with --reset 
if [ "$reset_script" = "true" ]; then
    
    # select the directory where all your program scripts are stored
    data_directory=$(zenity --file-selection --directory --title="Select your 'Program' folder" 2>/dev/null)

    # delete each file if they exist
    delete_file "$data_directory/backend.py"
    delete_file "$data_directory/main.py"
    delete_file "$data_directory/order_pad.py"
    delete_file "$data_directory/file_signatures.py"
fi

# install each file
install_program backend.py
install_program main.py
install_program order_pad.py
install_program file_signatures.py

script_dir="$( cd "$( dirname "${(%):-%N}" )" && pwd )" # save the directory the script is being ran from 

ini_files=( $(find "$script_dir" -name "*.ini") ) # list all the .ini files in the script directory 

if [ ${#ini_files[@]} -eq 0 ]; then # if there is no .ini files
    echo "No config.ini file found" 
    wait
    echo -n "Do you want to download config.ini from GitHub? (Y/n): " # allow the user to download a fresh one from github
    read download_config
    download_config=${download_config:-Y} # default the answer to the question as yes 

    if [ "$download_config" = "Y" ] || [ "$download_config" = "y" ]; then # if yes 
        install_program config.ini # install the config file from github
        echo "Downloaded config.ini from GitHub"
        config_file_found="true"
    else 
        echo -n "Exiting" # exit
        
        for i in {1..3}; do
            sleep 0.5
            echo -n "." 
        done

        echo    
        exit 1 # exit the script
    fi
else # if config files have been found 

    for ini_file in "${ini_files[@]}"; do
        if [ "$ini_file" != ""$script_dir"/config.ini" ]; then
            echo "Found .ini file at: $ini_file" # if the .ini file isn't named config.ini
            echo -n "Is this your config .ini file? (Y/n): " # ask if this the correct config file  
            wait    
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then # if it is then
                mv "$ini_file" "$script_dir/config.ini" # rename the file to config.ini
                echo "Renamed $ini_file to config.ini"
                config_file_found="true"
            fi
        else # if the file config.ini is found
            echo "config.ini found"
            config_file_found="true" 
        fi
    done
fi

wait

update_config_directory "data" # check if the data directory is valid and if it isn't select a new one
data_directory=$(sed -n 's/^data = [[:space:]]*//p' "config.ini") # save the data directory to a variable

update_config_directory "public_key_path" # run the function for the public and private key 
update_config_directory "private_key_path"

database_files=$(find "$data_directory" -type f -name "*.db") # list database files similar to how .ini files were listed 

if [ ${#database_files[@]} -eq 0 ]; then # if there is none
    echo "No database.db file found in the data directory"
    echo -n "Do you want to download database.db from GitHub? (Y/n): " # allow the user to download the latest version from github
    wait
    read download_db
    download_db=${download_db:-Y}
    if [ "$download_db" = "Y" ] || [ "$download_db" = "y" ]; then
        install_program database.db
        echo "Downloaded database.db from GitHub"
        wait
    else
        echo -n "Exiting" # exit
        
        for i in {1..3}; do
            sleep 0.5
            echo -n "." 
        done

        echo    
        exit 1 # exit the script
    fi
else
    for database_file in "${database_files[@]}"; do
        if [ "$database_file" != "$data_directory/database.db" ]; then
            echo "Found database.db file at: $database_file"
            echo -n "Is this your database file? (Y/n): " # otherwise ask the user to confirm which of the database files is theirs
            wait
            read confirm
            confirm=${confirm:-Y}
            if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                mv "$database_file" "$data_directory/database.db" # same process of renaming an incorrectly named database file after the user confirms which file is the correct one if any
                echo "Renamed $database_file to database.db"
            fi
        else
            echo "database.db found"
            wait
        fi
    done
fi

database_path=("$data_directory/database.db") # save the database path to a variable 

results=$(sqlite3 "$database_path" "SELECT * FROM passwords;") # get the current admin password using this SQL query 

if [ -z "$results" ]; then # if nothing is returned 
    echo "No admin password found"
    wait
    attempt=1
    valid_password # set a new password 
    sqlite3 "$database_path" "INSERT INTO passwords (admin_alias, hashed_password) VALUES ('$alias', '$hashed_password');" # insert it into the password table using SQL
fi

if [ -e "$script_dir/config.ini" ] && [ -e "$data_directory/database.db" ]; then # if the config file exists and the database file exists in the correct places 
    echo "Running without issues" # no issues 
    python3 "$script_dir/main.py" # run the main python script 
else
    echo "Necessary dependencies not found"
    wait    
    echo "Failed to run program" # otherwise alert the user that the program failed
    exit 127
fi
