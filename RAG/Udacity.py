def letterCombinations(digits):
        """
        :type digits: str
        :rtype: List[str]
        """
        list_= []
        dict= {2:["a","b","c"],3:["d","e","f"]}
        if len(digits)>1:
            
            A=dict[2]
            B=dict[3]
            for i in A:
                for j in B:
                    list_.append(i+j)
        elif len(digits)==1:
            list_=dict[digits[0]]
            for i in list_:
                list_.append(i)
        
        return list_
                    
combinations = letterCombinations("23")
print(combinations)