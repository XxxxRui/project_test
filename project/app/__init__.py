from flask import Flask
import os
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # 配置 app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secretkey104')
    
    # 设置 CSRF 保护
    csrf = CSRFProtect(app)
    
    # 确保实例文件夹存在
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 导入并初始化数据库
    from app.db_helper import init_db
    init_db()
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)

    return app