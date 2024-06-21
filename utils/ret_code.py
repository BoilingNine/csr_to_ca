from fastapi import status

# 返回码描述信息
CODE_DESC = {
    # 通用返回码
    status.HTTP_200_OK: 'success',
    status.HTTP_500_INTERNAL_SERVER_ERROR: 'Server is out of service, please try again later.'
}
