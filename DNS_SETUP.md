# DNS Configuration for lexcommand.ai

## Required DNS Records

Add these DNS records at your domain registrar or DNS provider:

### A Records (IPv4)
```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 300

Type: A  
Name: www
Value: YOUR_SERVER_IP
TTL: 300
```

### AAAA Records (IPv6 - if available)
```
Type: AAAA
Name: @
Value: YOUR_SERVER_IPV6
TTL: 300

Type: AAAA
Name: www  
Value: YOUR_SERVER_IPV6
TTL: 300
```

### Additional Subdomains (Optional)
```
Type: A
Name: api
Value: YOUR_SERVER_IP
TTL: 300

Type: A
Name: ide
Value: YOUR_SERVER_IP
TTL: 300
```

## Popular DNS Providers

### Cloudflare
1. Log into Cloudflare Dashboard
2. Select lexcommand.ai
3. Go to DNS tab
4. Add the A records above
5. Enable "Proxied" for DDoS protection (orange cloud)

### Namecheap
1. Log into Namecheap
2. Go to Domain List → Manage
3. Click "Advanced DNS"
4. Add A records with @ and www

### GoDaddy
1. Log into GoDaddy
2. Go to My Products → DNS
3. Click "Add" and create A records

### AWS Route 53
1. Go to Route 53 Console
2. Select your hosted zone
3. Create Record Set
4. Add A records

## Verification

After updating DNS (wait 5-30 minutes for propagation):

```bash
# Check DNS resolution
dig lexcommand.ai
dig www.lexcommand.ai

# Test with curl
curl -I https://lexcommand.ai
```

## SSL Certificate

The deployment script will automatically obtain SSL certificates from Let's Encrypt once DNS is configured correctly.

## Firewall Rules

Ensure these ports are open on your server:
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH)

```bash
# Using ufw
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## CDN Configuration (Optional)

For better global performance, consider using Cloudflare:

1. Point your domain to Cloudflare nameservers
2. Enable "Auto Minify" for JS/CSS/HTML
3. Set SSL/TLS to "Full (strict)"
4. Enable "Always Use HTTPS"
5. Configure Page Rules for caching

## Monitoring

After DNS is configured, set up monitoring:

1. **Uptime Monitoring**: Use services like UptimeRobot or Pingdom
2. **SSL Monitoring**: Monitor certificate expiration
3. **Performance**: Use GTmetrix or PageSpeed Insights

## Troubleshooting

### DNS Not Resolving
- Wait for TTL to expire (up to 48 hours)
- Clear DNS cache: `sudo systemd-resolve --flush-caches`
- Check with: `nslookup lexcommand.ai`

### SSL Certificate Issues
- Ensure DNS is pointing to correct IP
- Check Nginx is running: `sudo systemctl status nginx`
- Verify ports 80/443 are open
- Check certbot logs: `sudo journalctl -u certbot`

### 502 Bad Gateway
- Check LEX service: `sudo systemctl status lex-lexcommand`
- Verify app is running on port 8000
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`