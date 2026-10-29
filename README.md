# 术库课程分发仓库

编辑源：[ReductTech/intuitive-deep-learning · develop/modules](https://github.com/ReductTech/intuitive-deep-learning/tree/develop/modules)。请在源仓库编辑；这里仅用于课程同步、分发和平台读取。

`main` 包含课程、共享教学组件、课程自带素材及创作规范；原先默认分支保存在 `back`，不强推、不合并两边项目历史。

同步任务约每五分钟检查一次，GitHub 调度可能延迟，也可在 Actions 中手动运行。新增和修改自动同步，本轮不自动删除历史课程文件；目标独立改动会停止同步并报错。

- `modules/`：课程源码、目录与共享组件。
- `modules/<课程>/assets/`：该课程的图片、视频、缩略图和数据；上线通过 OSS/CDN 访问。
- `creator-skill/`：课程创作规范。
- `course-library.json`：课程和运行依赖清单。
- `source-lock.json`：确切来源提交及内容输入版本。

课程需要 React、相应第三方依赖和平台的计算 API；登录、业务数据库、审核和发布后端不在本仓库。平台使用 `IDL_COURSE_LIBRARY_ROOT` 和 `SHUKU_COURSE_ROOT` 指向同一固定提交快照，更新源码后重新构建前端。
