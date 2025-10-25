import pandas as pd
import numpy as np
from datetime import datetime

class FraudDetectionModel:
    def __init__(self, model):
        self.model = model
        # Store feature names from training
        self.feature_names = model.get_booster().feature_names if hasattr(model, 'get_booster') else None
        
    def prepare_features(self, user_input):
        """
        Convert user inputs to model-compatible features
        """
        features = {}
        
        # Transaction amount features
        amount = float(user_input['amount'])
        features['TransactionAmt'] = amount
        features['TransactionAmt_log'] = np.log1p(amount)
        features['TransactionAmt_decimal'] = amount - int(amount)
        
        # Card features
        card_mapping = {'visa': 1, 'mastercard': 2, 'amex': 3, 'discover': 4}
        features['card_type'] = card_mapping.get(user_input['cardType'], 0)
        features['card1'] = int(user_input['cardLast4'])
        
        # Device features
        device_mapping = {'mobile': 1, 'desktop': 0, 'tablet': 2}
        features['DeviceType'] = device_mapping.get(user_input['deviceType'], -1)
        
        # Email features
        email_domain = user_input['email'].split('@')[1] if '@' in user_input['email'] else 'unknown'
        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        features['email_common'] = 1 if email_domain in common_domains else 0
        
        # Location features
        country_mapping = {'US': 1, 'UK': 2, 'CA': 3, 'IN': 4, 'AU': 5, 'OTHER': 0}
        features['addr1'] = country_mapping.get(user_input['country'], 0)
        
        # Time features
        now = datetime.now()
        features['Transaction_hour'] = now.hour
        features['Transaction_day'] = now.weekday()
        
        # Add default values for remaining features
        # This is critical - your model expects specific number of features
        for i in range(1, 15):
            if f'C{i}' not in features:
                features[f'C{i}'] = -999
        
        for i in range(1, 16):
            if f'D{i}' not in features:
                features[f'D{i}'] = -999
        
        for i in range(1, 10):
            if f'M{i}' not in features:
                features[f'M{i}'] = -999
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        return df
    
    def predict(self, user_input):
        """
        Make fraud prediction using rule-based approach for better fraud detection
        """
        try:
            # Extract key features
            amount = float(user_input['amount'])
            card_type = user_input['cardType']
            device_type = user_input['deviceType']
            country = user_input['country']
            email = user_input['email']
            
            # Get current time
            now = datetime.now()
            current_hour = now.hour
            current_day = now.weekday()
            
            # Rule-based fraud detection with balanced scoring
            fraud_score = 0
            fraud_reasons = []
            
            # Amount-based scoring (more conservative)
            if amount > 5000:
                fraud_score += 35
                fraud_reasons.append("Extremely high transaction amount")
            elif amount > 2000:
                fraud_score += 25
                fraud_reasons.append("Very high transaction amount")
            elif amount > 1000:
                fraud_score += 15
                fraud_reasons.append("High transaction amount")
            elif amount > 500:
                fraud_score += 8
                fraud_reasons.append("Medium-high transaction amount")
            
            # Card type risk (reduced scoring)
            if card_type == 'discover':
                fraud_score += 12
                fraud_reasons.append("Discover card (higher risk)")
            elif card_type == 'amex':
                fraud_score += 5
                fraud_reasons.append("American Express card")
            
            # Device type risk (reduced scoring)
            if device_type == 'mobile':
                fraud_score += 8
                fraud_reasons.append("Mobile device transaction")
            elif device_type == 'tablet':
                fraud_score += 5
                fraud_reasons.append("Tablet device transaction")
            
            # International transactions (reduced scoring)
            if country != 'US':
                fraud_score += 12
                fraud_reasons.append("International transaction")
            
            # Unusual hours (more specific)
            if current_hour < 4 or current_hour > 23:
                fraud_score += 10
                fraud_reasons.append("Very unusual transaction time")
            elif current_hour < 6 or current_hour > 22:
                fraud_score += 5
                fraud_reasons.append("Unusual transaction time")
            
            # Weekend transactions (reduced scoring)
            if current_day >= 5:  # Saturday or Sunday
                fraud_score += 3
                fraud_reasons.append("Weekend transaction")
            
            # Email domain risk (reduced scoring)
            email_domain = email.split('@')[1] if '@' in email else 'unknown'
            common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com', 'icloud.com', 'live.com']
            if email_domain not in common_domains:
                fraud_score += 8
                fraud_reasons.append("Uncommon email domain")
            
            # Multiple risk factors (only for high-risk combinations)
            high_risk_factors = 0
            if amount > 1000:
                high_risk_factors += 1
            if card_type == 'discover':
                high_risk_factors += 1
            if country != 'US':
                high_risk_factors += 1
            if device_type == 'mobile':
                high_risk_factors += 1
            if current_hour < 6 or current_hour > 22:
                high_risk_factors += 1
            
            if high_risk_factors >= 3:
                fraud_score += 15
                fraud_reasons.append("Multiple high-risk factors detected")
            elif high_risk_factors >= 2:
                fraud_score += 8
                fraud_reasons.append("Multiple risk factors detected")
            
            # Determine if fraud (higher threshold)
            is_fraud = fraud_score >= 60  # Increased threshold for fraud detection
            
            # Calculate probabilities
            fraud_probability = min(fraud_score / 100, 0.95)  # Cap at 95%
            legitimate_probability = 1 - fraud_probability
            
            # Calculate confidence
            confidence = max(fraud_probability, legitimate_probability) * 100
            
            print(f"Fraud Score: {fraud_score}, Reasons: {fraud_reasons}")
            print(f"Prediction: {'FRAUD' if is_fraud else 'LEGITIMATE'}")
            
            return {
                'is_fraud': is_fraud,
                'fraud_probability': fraud_probability,
                'legitimate_probability': legitimate_probability,
                'confidence': confidence,
                'risk_score': fraud_score,
                'fraud_reasons': fraud_reasons
            }
        
        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}")