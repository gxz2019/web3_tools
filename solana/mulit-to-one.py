import json
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from solana.keypair import Keypair

# 读取配置文件
with open('config.json', 'r') as file:
    config = json.load(file)

# 连接到 Solana 节点
client = Client(config["rpc"])

# 将 SOL 转换为 lamports
def sol_to_lamports(sol_amount):
    return int(sol_amount * 1_000_000_000)

# 读取主账户信息
main_account_secret_key = config["main_account"]["private_key"]
main_account_transfer_amount = sol_to_lamports(config["main_account"]["transfer_amount"])

# 读取子账户信息
sub_accounts = config["sub_accounts"]

# 读取 gas 设置
priority_fee = sol_to_lamports(config["gas_settings"]["priority_fee"])

# 创建主账户 Keypair
main_account_keypair = Keypair.from_secret_key(bytes.fromhex(main_account_secret_key))

# 创建交易
transaction = Transaction()

# 多转一：每个子账户向主账户转账
for sub_account in sub_accounts:
    sub_account_secret_key = sub_account["private_key"]
    sub_account_transfer_amount = sol_to_lamports(sub_account["transfer_amount"])

    sub_account_keypair = Keypair.from_secret_key(bytes.fromhex(sub_account_secret_key))
    transaction.add(
        transfer(
            TransferParams(
                from_pubkey=sub_account_keypair.public_key,
                to_pubkey=main_account_keypair.public_key,
                lamports=sub_account_transfer_amount
            )
        )
    )


transaction.recent_blockhash = client.get_recent_blockhash()["result"]["value"]["blockhash"]
transaction.fee_payer = main_account_keypair.public_key

transaction.add_fee_priority(priority_fee)

# 发送交易
response = client.send_transaction(transaction, main_account_keypair)
print(f"Transaction response: {response}")
