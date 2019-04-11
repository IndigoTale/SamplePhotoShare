from flask import render_template
import boto3


def signUpCheck(username, email, password, repeat_password):
    # コード
    # 0 異常なし
    # 1 再入力パスワードが一致しない
    # 2 同じUsernameが存在
    # 3 同じメールアドレスが存在
    if password != repeat_password:
        return render_template("signup.html", code=1)
    boto3.client("")


try:
    response = table.get_item(
        Key={
            'year': year,
            'title': title
        }
    )
except ClientError as e:
    print(e.response['Error']['Message'])
else:
    item = response['Item']
    print("GetItem succeeded:")
    print(json.dumps(item, indent=4, cls=DecimalEncoder))
