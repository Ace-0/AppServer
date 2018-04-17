# AppServer
Server that provides RESTful API services.

## 后台架构
![](https://raw.githubusercontent.com/TheYelda/AppServer/master/doc/architecture.png)
项目后台采用的技术栈为Nginx+Flask+MySQL。
- Nginx：高性能的Web服务器，向前端提供静态文件服务，同时针对Flask提供的RESTful API服务实现反向代理。
- Flask：轻量级Web应用框架，通过ORM（Object Relational Mapping，对象关系映射）技术更方便地操作MySQL。
- MySQL：最流行的关系型数据库管理系统，直接面向数据进行管理。

## 安装&运行
TODO

## 数据模型
TODO

## RESTful API
通过在线工具查看：
<https://agendaservice2.docs.apiary.io/#>
