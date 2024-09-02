from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# 定义常用搜索引擎的域名
COMMON_SEARCH_ENGINES = ["google.", "baidu.", "bing.", "wikipedia.", "yahoo.", "duckduckgo.","apple."]

def search_duckduckgo(query, output_file):
    chrome_driver_path = './chromedriver'  # 请根据您的系统设置正确的路径
    options = webdriver.ChromeOptions()
    driver = None
    results = []  # 存储结果
    try:
        print(f"启动浏览器并搜索: {query}")
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        
        driver.get(f"https://duckduckgo.com/?q={query}")
        
        print("等待页面加载...")
        WebDriverWait(driver, 30).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        time.sleep(2)  # 等待一些时间，确保元素加载完成

        # 解析搜索结果，仅匹配 rel="noopener" 的 a 标签
        search_results = driver.find_elements(By.CSS_SELECTOR, 'a[rel="noopener"]')

        print(f"找到 {len(search_results)} 个搜索结果")  # 打印找到的结果数量

        for result in search_results:
            try:
                title = result.text
                link = result.get_attribute('href')
                domain = urlparse(link).netloc  # 获取域名
                
                # 过滤掉常用搜索引擎的域名
                if any(engine in domain for engine in COMMON_SEARCH_ENGINES): # type: ignore
                    continue
                
                results.append({'Title': title, 'Link': link})

            except Exception as inner_e:
                print(f"在处理结果时发生错误: {inner_e}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            driver.quit()  # 关闭浏览器
    
    return results  # 返回结果


def main():
    input_file = 'queries.txt'  # 存放查询的文本文件
    output_file = 'filtered_search_results.csv'  # 输出的 CSV 文件
    
    # 创建 CSV 文件并写入表头（只写一次）
    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Title', 'Link'])
        writer.writeheader()  # 写入表头
    
    # 使用线程池，每次最多处理 5 个线程
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        
        # 从文件中读取每一行作为查询
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = f.readlines()
            for query in queries:
                query = query.strip()  # 去掉多余的空格和换行符
                if query:  # 如果查询不为空
                    futures.append(executor.submit(search_duckduckgo, query, output_file))
        
        # 等待所有线程完成并写入结果
        for future in futures:
            results = future.result()  # 等待结果
            # 将结果写入 CSV
            with open(output_file, mode='a', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['Title', 'Link'])
                for result in results:
                    writer.writerow(result)  # 写入每个匹配结果到 CSV

if __name__ == "__main__":
    main()
