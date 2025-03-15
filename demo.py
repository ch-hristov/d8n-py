from d8n.d8nClient import d8nClient
client = d8nClient("MY-API-KEY")

request = client.from_local_file("./large.jpg")
result_document = client.wait_till_completed(request['id'], print_debug_info=True)

for task in result_document.task_list:
    print(task)
    print(results)
