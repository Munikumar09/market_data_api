#!/bin/bash

# Function to print messages with colors
echo_info() {
  echo -e "\e[34m[INFO]\e[0m $1"
}
echo_error() {
  echo -e "\e[31m[ERROR]\e[0m $1"
}
echo_success() {
  echo -e "\e[32m[SUCCESS]\e[0m $1"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" > /dev/null 2>&1
}

# Function to install Flutter and related tools
install_flutter_tools() {
  echo_info "Updating system packages..."
  if ! sudo apt-get update; then
    echo_error "Failed to update system packages."
    exit 1
  fi

  echo_info "Installing dependencies..."
  if ! sudo apt-get install -y curl git unzip xz-utils zip libglu1-mesa; then
    echo_error "Failed to install dependencies."
    exit 1
  fi

  echo_info "Installing Flutter..."
  if [ ! -d "$HOME/flutter" ]; then
    if ! git clone https://github.com/flutter/flutter.git -b stable $HOME/flutter; then
      echo_error "Failed to clone Flutter repository."
      exit 1
    fi
  fi

  echo_info "Adding Flutter to PATH..."
  export PATH="$HOME/flutter/bin:$PATH"
  if ! grep -q "flutter/bin" ~/.bashrc; then
    echo "export PATH=\"$HOME/flutter/bin:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
  fi

  echo_info "Installing Android SDK Command-line Tools..."
  if ! sudo apt-get install -y android-sdk; then
    echo_error "Failed to install Android SDK."
    exit 1
  fi

  echo_info "Installing Android Emulator and Platform Tools..."
  if ! yes | sdkmanager --install "emulator" "platform-tools" "platforms;android-33"; then
    echo_error "Failed to install Android Emulator and Platform Tools."
    exit 1
  fi

  echo_info "Setting up Android environment variables..."
  export ANDROID_HOME="$HOME/Android/Sdk"
  export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
  if ! grep -q "Android/Sdk" ~/.bashrc; then
    echo "export ANDROID_HOME=\"$HOME/Android/Sdk\"" >> ~/.bashrc
    echo "export PATH=\"$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
  fi

  echo_info "Setting up Flutter environment..."
  if ! flutter doctor; then
    echo_error "Flutter setup failed."
    exit 1
  fi

  echo_success "Flutter and related tools were installed and configured successfully! You can now use an Android emulator or connect your Android device."
}

# Function to uninstall Flutter and related tools
uninstall_flutter_tools() {
  echo_info "Removing Flutter..."
  if [ -d "$HOME/flutter" ]; then
    if ! rm -rf $HOME/flutter; then
      echo_error "Failed to remove Flutter."
      exit 1
    fi
  fi

  echo_info "Uninstalling Android SDK..."
  if ! sudo apt-get remove --purge -y android-sdk; then
    echo_error "Failed to uninstall Android SDK."
    exit 1
  fi

  echo_info "Cleaning up configuration files..."
  if ! sed -i '/flutter\/bin/d' ~/.bashrc || ! sed -i '/Android\/Sdk/d' ~/.bashrc; then
    echo_error "Failed to clean up configuration files."
    exit 1
  fi
  source ~/.bashrc

  echo_success "Flutter and related tools were uninstalled successfully!"
}

# Main script logic
if [ "$#" -eq 0 ]; then
  echo_error "No flag provided. Use --install to install Flutter tools or --uninstall to remove them."
  exit 1
fi

case "$1" in
  --install)
    install_flutter_tools
    ;;
  --uninstall)
    uninstall_flutter_tools
    ;;
  *)
    echo_error "Invalid flag provided. Use --install to install Flutter tools or --uninstall to remove them."
    exit 1
    ;;
esac
