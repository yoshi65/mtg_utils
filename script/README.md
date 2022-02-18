# script

## get_hare_name

Get hareruya page name.

### Example
```sh
% python get_hare_name.py 'https://www.hareruyamtg.com/ja/products/detail/69767?lang=EN'
【Foil】《スカラベの神/The Scarab God》[MPS] 金 : 25,000
```

## draw_total_price_timelapse
Draw total price timelapse using column `total price` in dynamodb.
The column is updated by [NotifyPriceChange](../NotifyPriceChange) every Monday.
```sh
python draw_total_price_timelapse.py
```
