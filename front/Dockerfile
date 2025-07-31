# 构建阶段
FROM node:18.18-alpine as builder

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN addgroup -S unitree && adduser -S unitree -G unitree

# 设置npm镜像
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g pnpm && \
    pnpm config set registry https://registry.npmmirror.com

# 复制package文件
COPY package.json pnpm-lock.yaml ./

# 设置目录权限
RUN chown -R unitree:unitree /app

# 切换到非root用户
USER unitree

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制应用代码
COPY --chown=unitree:unitree . .

# 构建应用
ENV NODE_ENV=production
RUN pnpm build

# 生产阶段
FROM nginx:stable-alpine

# 创建非root用户
RUN addgroup -S unitree && adduser -S unitree -G unitree

# 设置时区为中国时区
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物到nginx目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 设置nginx目录权限
RUN chown -R unitree:unitree /usr/share/nginx/html && \
    chown -R unitree:unitree /var/cache/nginx && \
    chown -R unitree:unitree /var/log/nginx && \
    chown -R unitree:unitree /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R unitree:unitree /var/run/nginx.pid

# 修改nginx配置以使用非root用户
RUN sed -i 's/user  nginx/user  unitree/g' /etc/nginx/nginx.conf

# 切换到非root用户
USER unitree

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]