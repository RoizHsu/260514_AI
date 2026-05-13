#!/usr/bin/env python
"""
生成自簽名 SSL 證書用於本地開發
Run: python generate_ssl.py
"""

from pathlib import Path
import subprocess
import sys

def generate_with_cryptography():
    """使用 cryptography 庫生成 SSL 證書"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        print("📦 使用 Python cryptography 庫生成證書...")
        
        # 生成私鑰
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # 創建證書主題
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"TW"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Taiwan"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Taipei"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Local"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        # 構建證書
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost"),
                    x509.DNSName(u"127.0.0.1"),
                    x509.DNSName(u"0.0.0.0"),
                ]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )
        
        # 保存證書和私鑰
        cert_dir = Path("ssl")
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "cert.pem"
        key_file = cert_dir / "key.pem"
        
        # 寫入證書
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # 寫入私鑰
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ SSL 證書已生成：")
        print(f"   - {cert_file}")
        print(f"   - {key_file}")
        return str(cert_file), str(key_file)
        
    except ImportError:
        print("❌ 請先安裝 cryptography 庫：")
        print("   pip install cryptography")
        return None, None


def generate_with_openssl():
    """使用 openssl 命令行工具生成 SSL 證書"""
    cert_dir = Path("ssl")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # 如果證書已存在，不重新生成
    if cert_file.exists() and key_file.exists():
        print("✅ SSL 證書已存在")
        return str(cert_file), str(key_file)
    
    print("🔐 正在生成 SSL 證書...")
    
    # 使用 openssl 生成自簽名證書（365天有效期）
    command = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", "365",
        "-nodes",
        "-subj", "/C=TW/ST=Taiwan/L=Taipei/O=Local/CN=localhost"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"✅ 證書已生成：")
        print(f"   - {cert_file}")
        print(f"   - {key_file}")
        return str(cert_file), str(key_file)
    except FileNotFoundError:
        print("❌ openssl 未安裝")
        return None, None
    except subprocess.CalledProcessError as e:
        print(f"❌ 生成失敗: {e}")
        return None, None


def generate_ssl_certificate():
    """生成自簽名 SSL 證書"""
    cert_dir = Path("ssl")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # 如果證書已存在，不重新生成
    if cert_file.exists() and key_file.exists():
        print("✅ SSL 證書已存在")
        return str(cert_file), str(key_file)
    
    # 先嘗試用 cryptography 庫
    cert, key = generate_with_cryptography()
    if cert and key:
        return cert, key
    
    # 如果失敗，嘗試 openssl
    print("\n嘗試使用 openssl...")
    cert, key = generate_with_openssl()
    if cert and key:
        return cert, key
    
    print("\n❌ 無法生成 SSL 證書")
    print("請選擇以下方式之一：")
    print("  1. 安裝 cryptography: pip install cryptography")
    print("  2. 安裝 openssl (Windows 用 choco install openssl 或從 https://slproweb.com/products/Win32OpenSSL.html 下載)")
    print("  3. 在 Docker 中運行（會自動生成）")
    sys.exit(1)


if __name__ == "__main__":
    cert, key = generate_ssl_certificate()
