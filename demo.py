from d8n.d8nClient import d8nClient
client = d8nClient("MY-API-KEY")

request = client.from_local_file("./symbols.jpg")
client.wait_till_completed(request.id, print_debug_info=True)
results = client.get_completed(request.id)
download = client.get_line_image(request.id)

download.show()
