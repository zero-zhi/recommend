#! /usr/bin/env python
# -*- coding: utf-8 -*-
import search_tool

# 爬取数据并在本地建立数据库
search_tool.crawl_data()
while True:
    # 显示功能菜单
    search_tool.showMenu()
    operation = input("请输入操作选项序号：")
    print("您选择的操作是【%s】" % operation)

    if operation in ["1", "2", "3", "4"]:
        # Id搜索
        if operation == "1":
            id_num = input("请输入搜索标题：")
            search_tool.searchId(id_num)
        # 标题搜索
        elif operation == "2":
            title = input("请输入搜索标题：")
            search_tool.searchTitle(title)
        # 内容搜索
        elif operation == "3":
            content = input("请输入搜索内容：")
            search_tool.searchContent(content)
        # 内容推荐
        elif operation == "4":
            s = input("请输入希望匹配的文章绝对路径：")
            search_tool.recommendContent(s)
    # 退出系统
    elif operation == "0":
        print("已退出，欢迎再次使用【搜索推荐系统】")
        break
    else:
        print("您的输入不正确，请重新输入")
