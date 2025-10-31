# 🔗 BTC Blocktime Randomization Feature

## Overview

The Auto-Typer Pro now includes a unique feature that uses **Bitcoin blockchain data** to randomize typing intervals, making your automation truly unpredictable and more natural-looking!

---

## Why Use BTC Blocktime?

Traditional randomization uses pseudo-random number generators which can be predictable. Using Bitcoin blocktime provides:

✅ **Truly unpredictable** - Based on real-world blockchain data
✅ **Changes naturally** - New block every ~10 minutes
✅ **Decentralized source** - No single point of control
✅ **More human-like** - Organic variation patterns
✅ **Verifiable** - You can check the blockchain yourself

---

## How It Works

The script fetches the latest Bitcoin block from the blockchain.info API and uses the block data to calculate intervals:

1. **Fetches** the latest BTC block (height, timestamp, hash)
2. **Extracts** randomization seed from block data
3. **Calculates** interval based on your chosen mode
4. **Refreshes** block data every 5 commands to get new blocks

---

## Randomization Modes

### 🔢 1 Digit Mode (last_digit)
- Uses the **last digit** of the block height (0-9)
- Creates **95% to 115%** variation of base interval
- **Example:**
  - Base interval: 10 seconds
  - Block #876,543 → last digit: 3
  - Calculated interval: ~10.6 seconds

### 🔢🔢 2 Digits Mode (last_two_digits)
- Uses the **last 2 digits** of block height (0-99)
- Creates **50% to 150%** variation of base interval
- **More variation** than 1 digit mode
- **Example:**
  - Base interval: 10 seconds
  - Block #876,543 → last 2 digits: 43
  - Calculated interval: ~9.3 seconds

### ⏰ Time Mode (timestamp_modulo)
- Uses the **block timestamp modulo 100**
- Creates **70% to 130%** variation of base interval
- Changes more frequently as timestamps vary more
- **Example:**
  - Base interval: 10 seconds
  - Block timestamp: 1735483210 → mod 100: 10
  - Calculated interval: ~7.6 seconds

---

## Usage Instructions

### Step 1: Enable BTC Randomization
1. Open Auto-Typer Pro
2. In **Advanced Options**, check **"🔗 Use BTC blocktime for randomization"**
3. The script will automatically fetch the latest block

### Step 2: Choose Mode
Select one of three modes:
- **1 digit** - Subtle variation (recommended for most uses)
- **2 digits** - Medium variation
- **Time** - More variation based on timestamps

### Step 3: Check Status
- Look at **"Block: #XXXXXX"** to see the current block
- Click **🔄** to manually refresh block data
- The log will show which block is being used

### Step 4: Start Typing
- Configure your commands and interval as usual
- The BTC randomization will automatically apply
- Log messages will show: `BTC Block #876543 → last digit: 3 → interval: 10.6s`

---

## Examples

### Example 1: Subtle Randomization
```
Base interval: 5 seconds
Mode: 1 digit
Block #876,543

Result: 5.0s to 5.75s intervals
Pattern: Slowly changes every ~10 minutes (new block)
```

### Example 2: High Variation
```
Base interval: 10 seconds
Mode: 2 digits
Block #876,543

Result: 5.0s to 15.0s intervals
Pattern: Wide variation, more unpredictable
```

### Example 3: Time-Based
```
Base interval: 30 seconds
Mode: Time
Block timestamp: 1735483210

Result: 21s to 39s intervals
Pattern: Based on block creation time
```

---

## Technical Details

### API Used
- **Endpoint:** `https://blockchain.info/latestblock`
- **Response:** JSON with block height, timestamp, and hash
- **Update frequency:** Script fetches new data every 5 commands
- **Timeout:** 10 seconds

### Block Refresh Strategy
- Initial fetch when you enable the feature
- Auto-refresh every 5 commands during operation
- Manual refresh via 🔄 button
- Falls back to standard random if fetch fails

### Network Requirements
- Requires internet connection
- Uses HTTPS (secure)
- Minimal bandwidth (~1KB per request)
- Graceful fallback if blockchain.info is unreachable

---

## Comparison with Standard Randomization

| Feature | Standard Random | BTC Blocktime |
|---------|----------------|---------------|
| **Predictability** | Pseudo-random | Truly unpredictable |
| **Source** | Computer algorithm | Bitcoin blockchain |
| **Variation** | ±20% fixed | 5% to 50% depending on mode |
| **Updates** | Every command | Every ~10 min (new block) |
| **Internet** | Not required | Required |
| **Fallback** | N/A | Falls back to standard if offline |

---

## Tips & Best Practices

### 🎯 Recommended Settings

**For subtle, natural variation:**
```
Interval: 5-10 seconds
Mode: 1 digit
Result: Very human-like, small variations
```

**For unpredictable timing:**
```
Interval: 30 seconds
Mode: 2 digits
Result: High variation, hard to predict
```

**For time-sensitive randomization:**
```
Interval: Any
Mode: Time
Result: Based on block timestamp
```

### 💡 Pro Tips

1. **Combine with command randomization** for maximum unpredictability
2. **Use 1 digit mode** if you want consistent but varied timing
3. **Use 2 digits mode** for maximum randomness
4. **Check the log** to see exactly how blocks affect your intervals
5. **Manual refresh** the block if you want to change the pattern immediately

### ⚠️ Notes

- BTC randomization **replaces** the standard random delay (±20%)
- You cannot use both BTC randomization and standard random delay at the same time
- Block data is cached and reused until refresh
- New blocks appear approximately every 10 minutes
- If the API is down, it falls back to standard randomization

---

## Troubleshooting

### Block shows "Not fetched"
- Check your internet connection
- Click the 🔄 refresh button
- Check if blockchain.info is accessible
- Script will use standard random as fallback

### Interval seems constant
- Check if BTC randomization is actually enabled (checkbox)
- Look at the log - it shows the calculation
- New blocks only appear every ~10 minutes
- Try clicking 🔄 to force a refresh

### "Failed to fetch BTC block" error
- Internet connection issue
- blockchain.info API temporarily down
- Firewall blocking the request
- Script automatically falls back to standard random

---

## Example Log Output

```
[14:23:15] INFO: Fetching latest BTC block...
[14:23:16] SUCCESS: ✓ BTC Block #876543 at 14:22:10
[14:23:16] INFO: Typing: 'go on'
[14:23:17] SUCCESS: ✓ Command sent successfully (#1)
[14:23:17] INFO: BTC Block #876543 → last digit: 3 → interval: 10.6s
[14:23:17] INFO: Waiting 10.6s until next command...
[14:23:28] INFO: Typing: 'continue'
[14:23:29] SUCCESS: ✓ Command sent successfully (#2)
[14:23:29] INFO: BTC Block #876543 → last digit: 3 → interval: 10.6s
[14:23:29] INFO: Waiting 10.6s until next command...
```

---

## Advanced: Understanding the Math

### 1 Digit Mode
```python
last_digit = block_height % 10  # 0-9
variation = last_digit / 100.0   # 0.00 to 0.09
multiplier = 0.95 + (variation * 2)  # 0.95 to 1.15
interval = base_interval * multiplier
```

### 2 Digits Mode
```python
last_two = block_height % 100    # 0-99
variation = last_two / 100.0      # 0.00 to 0.99
multiplier = 0.5 + variation      # 0.50 to 1.50
interval = base_interval * multiplier
```

### Time Mode
```python
timestamp_mod = block_timestamp % 100  # 0-99
variation = timestamp_mod / 100.0       # 0.00 to 0.99
multiplier = 0.7 + (variation * 0.6)   # 0.70 to 1.30
interval = base_interval * multiplier
```

---

## Fun Facts

- Bitcoin blocks are mined approximately every 10 minutes
- Each block has a unique height (incrementing number)
- Block timestamps are set by miners
- The blockchain is public and verifiable
- Using blockchain data makes your automation truly non-deterministic!

---

## Future Enhancements

Possible future additions:
- Use block hash for even more randomization
- Support other blockchains (ETH, LTC, etc.)
- Use multiple blocks for rolling average
- Visualize block-based timing patterns
- Add block difficulty as a factor

---

**Enjoy truly unpredictable automation powered by Bitcoin! 🔗⛓️**
