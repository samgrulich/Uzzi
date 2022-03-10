import requests

def request(url:str, **kwargs):
    return requests.get(url, **kwargs)

def main():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': 'cf_chl_2=455c185865e853b; cf_chl_prog=x12; cf_clearance=WdY29hAS9Zh2yL3cxhWbz0zmJhY6peLz4BLNAJqLoaw-1646810504-0-150; XSRF-TOKEN=eyJpdiI6IkdSa3FVL3M2NFVNQU54b2FrZjJnWXc9PSIsInZhbHVlIjoiMy9uck00Tldpb0lPcG9HRS8yZ0Fsc3cva1lWSnlvTEtEY2ZzaGMzZTlXajZaN2w4Z0Z2VDhrazVDbXdyUWRYa0pOM1FtQXc2Mk9YYjhyODRtMFUyVnYzL0FkR1NxVytWeWQwNEJ2UVU5cHRUV21VdUEzZ1pXMUJYU3N0MGtwaUciLCJtYWMiOiI3OGMzZDc5NzUyMzk4NTU5NTFkZTExYzNiZmQ3YjUxYjYxNjYwMzFkMmEyMWM4OTgyYjIzY2JlZWY1Y2I1ZTNmIiwidGFnIjoiIn0%3D; howrareis_session=eyJpdiI6Ikxucm5uOXdzTkkvYnhFdUZiTjJDdHc9PSIsInZhbHVlIjoiaWsvcVZEa1UwWU45NnBzWlU0RnFEVXl2U0RKYytka0d0Y3dOeXE5dU9sSFFYdDYrTXpNeGdYR3Y1cFlRdWhVZ2JFVE9mTGNCOEhOVHNkZVMwRURhNlJENGEzTUxvL3p2bDMwYTc0Q2FNL05RTzBsZ2poQjNWSnByNE8rR2JvWjciLCJtYWMiOiJmMGUzZTNkZTk0M2Q5YjI0ZmUyMDg5YzFhMDMyNDI5YzdmZDY3NzBmNGUzNzRkMDEyYTViM2VkZGQ5NmEwNjJhIiwidGFnIjoiIn0%3D',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }

    url = 'https://howrare.is/api/v0.1/collections'

    response = request(url, headers=headers)

    print(response.status_code)

main()