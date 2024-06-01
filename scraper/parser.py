def parse_table(table, direction):
    ida_data = []

    if table is None:
        return ida_data
    for row in table:
        train = {}
        try:
            train['departure'] = row.select(".trenes > h5:first-of-type")[0].text.strip()
        except:
            train['departure'] = "N/A"
        try:
            train['arrival'] = row.select(".trenes > h5:last-of-type")[0].text.strip()
        except:
            train['arrival'] = "N/A"
        train['train_type'] = "undefined"
        # they are not rendering the train type properly, I am not doing crap to parse it
        """
        try:
            train['train_type'] = row.find('div', id=f'dtipotren{row["cdgotren"]}').text.strip()
            if train['train_type'] == "":
                train['train_type'] = row.find('div', id=f'dtipotren{row["cdgotren"]}').find('img')['alt']
        except:
            train['train_type'] = "N/A"
        """
        try:
            train['price'] = row.select('.precio-final')[0].contents[1].strip()
            train['price'] = float(train['price'].replace(" €", "").replace(",", "."))
            train['status'] = "available"
        except:
            train['price'] = 0
            train['status'] = "full"
        train['direction'] = direction
        ida_data.append(train)

    return ida_data
