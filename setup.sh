#!/bin/zsh

if ! yay -Qq python3 &>/dev/null; then
    echo "Python is not installed. Installing Python..."
    sudo pacman -S python3
    echo "Python has been installed."
else
    echo "Python is already installed."
fi

if ! yay -Qq python-tkcalendar &>/dev/null; then
    echo "Installing python-tkcalendar..."
    yay -S --noconfirm python-tkcalendar
    echo "python-tkcalendar has been installed."
else
    echo "python-tkcalendar is already installed."
fi

if ! yay -Qq python-docx &>/dev/null; then
    echo "Installing python-docx..."
    yay -S --noconfirm python-docx
    echo "python-docx has been installed."
else
    echo "python-docx is already installed."
fi

if ! yay -Qq sqlite3 &>/dev/null; then
    echo "Installing sqlite3..."
    yay -S --noconfirm sqlite3
    echo "sqlite3 has been installed."
else
    echo "sqlite3 is already installed."
fi

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -d "$script_dir" ]; then
    config_files=( $(find "$script_dir" -name "config.ini") )
    database_files=( $(find "$script_dir" -name "database.db") )

    if [ ${#config_files[@]} -eq 0 ]; then
        echo "config.ini file not found in the script's directory."
        echo "The program will not run as intended"
    else
        for config_file in "${config_files[@]}"; do
            if [ "$config_file" != "$script_dir/config.ini" ]; then
                echo "Found initialisation file at: $config_file"
                echo -n "Is this your config file? (Y/n): "
                read confirm
                confirm=${confirm:-Y}
                if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                    mv "$config_file" "$script_dir/config.ini"
                    echo "Renamed $config_file to config.ini"
                fi
            else
                echo "config.ini found."
            fi
        done
    fi

    if [ ${#database_files[@]} -eq 0 ]; then
        echo "database.db file not found in the script's directory."
        echo "The program will not run as intended"
    else
        for database_file in "${database_files[@]}"; do
            if [ "$database_file" != "$script_dir/database.db" ]; then
                echo "Found database file at: $database_file"
                echo -n "Is this your database file? (Y/n): "
                read confirm
                confirm=${confirm:-Y}
                if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
                    mv "$database_file" "$script_dir/database.db"
                    echo "Renamed $database_file to database.db"
                fi
            else
                echo "database.db found."
            fi
        done
    fi
else
    echo "An unknown error occurred while setting up the program."
fi

