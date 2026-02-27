# Custom QR Code Generator (Python)

A fully functional, scratch-built QR Code generator written in pure Python. This project was created to demonstrate a deep understanding of QR matrix mathematics, error correction, and byte-level data manipulation without relying on pre-built QR libraries.

## 🚀 Features

* **Custom Matrix Generation:** Dynamically builds the QR grid (supports Versions 1-4).
* **Smart Data Routing:** Custom algorithm for the data "snake" to bypass alignment, formatting, and timing patterns.
* **Error Correction:** Integrated Reed-Solomon (Level L) encoding to ensure scannability.
* **Format & Masking:** Accurately applies standard QR masking and format information bits.
* **Interactive CLI:** Easy-to-use terminal interface for generating codes on the fly.
* **Optimized Rendering:** Uses `Pillow` (ImageDraw) for fast, pixel-perfect, and crisp PNG export.

## 🛠️ Requirements

To run this project, you need Python installed on your system along with the following libraries:

* `reedsolo`
* `Pillow`

## ⚙️ Installation

1. Clone this repository to your local machine:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/qr-code-engine.git](https://github.com/YOUR_USERNAME/qr-code-engine.git)
   cd qr-code-engine
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

Run the script directly from your terminal:

```bash
python genQR.py
```

The interactive prompt will ask for:
1. The link or text you want to encode.
2. Your desired filename.

The generated QR code will be previewed in the terminal and saved as a crisp, scannable `.png` file in your directory.
