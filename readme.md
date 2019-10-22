


### 安装步骤

1. 安装wkhtmltopdf

   不建议使用包管理工具安装, 因为这样安装的版本可能不是最新的, 而旧版的wkhtmltopdf对中文的支持不太好, 建议从官网下载最新的安装器安装, 下载地址https://wkhtmltopdf.org/downloads.html. windows下直接installer进行安装, centos下载rpm包:

   ```bash
   $ yum install xorg-x11-fonts-75dpi
   $ rpm -ivh wkhtmltox-0.12.5-1.centos7.x86_64.rpm
   ```

2. 安装本项目(python3.7)

   ```bash
   $ cd crawl_greek_time
   $ python setup.py install
   ```

   

### 开始爬虫

1. 查看帮助信息

   ```bash
   $ greek-time-crawler
   Usage: greek-time-crawler [options]
   
   Options:
     -h, --help            show this help message and exit
     --cell-phone=CELL_PHONE
                           cell phone to login greek time
     --password=PASSWORD   password to login greek time
     --save-dir=SAVE_DIR   directory to save pdf
     --download-interval=DOWNLOAD_INTERVAL
                           interval of every request
   ```

   

2. 开始爬虫

   ```
   greek-time-crawler --cell-phone=手机号 --password=密码 --save-dir=pdf保存的目录
   ```

   