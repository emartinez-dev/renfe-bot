def parse_table(table, direction):
    ida_data = []

    if table is None:
        return ida_data
    for row in table:
        train = {}
        try:
            train['departure'] = row.find('div', class_='salida').text.strip()
        except:
            train['departure'] = "N/A"
        try:
            train['arrival'] = row.find('div', class_='llegada').text.strip()
        except:
            train['arrival'] = "N/A"
        try:
            train['train_type'] = row.find('div', id=f'dtipotren{row["cdgotren"]}').text.strip()
            if train['train_type'] == "":
                train['train_type'] = row.find('div', id=f'dtipotren{row["cdgotren"]}').find('img')['alt']
        except:
            train['train_type'] = "N/A"
        try:
            train['price'] = row.find('div', class_='precio booking-list-element-big-font').text.strip()
            train['price'] = float(train['price'].replace(" €", "").replace(",", "."))
            train['status'] = "available"
        except:
            train['price'] = 0
            train['status'] = "full"
        train['direction'] = direction
        ida_data.append(train)

    return ida_data
