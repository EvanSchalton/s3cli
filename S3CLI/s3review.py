import os
from .s3connection import connect
import pandas as pd
import json
from tabulate import tabulate
from .utils import convertbyte

class s3Reviewer:
    """Custom s3client wrapper to expose desired metrics"""
    def __init__(self, configPath="", preload = False):
        self.s3 = connect(configPath)
        if preload:
            self.preloadBuckets()

    @property
    def buckets(self):
        """Returns a list of bucket objects"""
        try:
            return list(self.__buckets.values())
        except AttributeError:
            self.fetchBuckets()
            return list(self.__buckets.values())

    @property
    def list(self):
        """Returns a list of bucket names"""
        try:
            return list(self.__buckets.keys())
        except AttributeError:
            self.fetchBuckets()
            return list(self.__buckets.keys())

    def fetchBuckets(self):
        """initializes the bucket class for each bucket the user has access to"""
        self.__buckets = {bucket.name:Bucket(bucket) for bucket in self.s3.buckets.all()}
        return self.__buckets

    def getBucket(self, bucketName):
        """returns the provided bucket"""
        try:
            return self.__buckets[bucketName]
        except AttributeError:
            self.fetchBuckets()
            return self.__buckets[bucketName]

    def preloadBuckets(self):
        """captures all bucket detail"""
        for bucket in self.buckets:
            bucket.calculate()

    def table(self, unit="byte", refresh=False):
        """Creates and applies unit mask to table"""
        if refresh:
            self.preloadBuckets()

        def updateDF(df, unit):
            colOrder = ['name', 'creation_date', 'count', 'size', 'last_modified']
            df = df[colOrder]
            df['size'] = df['size'].apply(lambda x: convertbyte(x, unit))
            df['creation_date'] = df['creation_date'].apply(lambda x: str(x))
            df['last_modified'] = df['last_modified'].apply(lambda x: str(x))

            df.columns = [f"size ({unit})" if i == "size" else i for i in colOrder]
            return df

        try:
            return updateDF(self.__table, unit)
        except AttributeError:
            self.__table = pd.DataFrame([bucket.details() for bucket in self.buckets])
            return updateDF(self.__table, unit)

    def showDetails(self, unit="byte", refresh=False):
        """prints a ascii table to the console"""
        try:
            tableString = tabulate(
                self.table(unit=unit, refresh=refresh),
                headers='keys',
                tablefmt='psql',
                showindex=False
            )
            print(tableString)
            return True
        except:
            return False

    def saveDetailTable(self, path, unit="byte", refresh=False):
        """saves the output table to the provided location"""

        try:
            df = self.table(unit=unit, refresh=refresh)
            if ".xls" in path:
                df.to_excel(path, index=False)
            else:
                df.to_csv(path, index=False)
            return True
        except Exception as e:
            print("e", e)
            return False


class Bucket:

    def __init__(self, s3BucketObject):
        self.s3BucketObject = s3BucketObject

    @property
    def name(self):
        return self.s3BucketObject.name

    @property
    def creation_date(self):
        return self.s3BucketObject.creation_date

    @property
    def objects(self):
        try:
            return self.__objects
        except AttributeError:
            self.__objects = self.s3BucketObject.objects
            return self.__objects

    def calculate(self):
        size = 0
        last_modified = self.creation_date
        count = 0
        for item in self.objects.all():
            size += item.size
            modified = item.last_modified
            if modified > last_modified:
                last_modified = modified
            count += 1

        self.__size = size
        self.__count = count
        self.__last_modified = last_modified

    @property
    def count(self):
        try:
            return self.__count
        except AttributeError:
            self.calculate()
            return self.__count

    def size(self, unit="byte"):
        try:
            return convertbyte(self.__size, unit)
        except AttributeError:
            self.calculate()
            return convertbyte(self.__size, unit)

    @property
    def last_modified(self):
        try:
            return self.__last_modified
        except AttributeError:
            self.calculate()
            return self.__last_modified

    def details(self, unit="byte", calculate=False, asString=False):
        if calculate:
            self.calculate()

        output = {
            "name": self.name,
            "creation_date": self.creation_date,
            "count": self.count,
            "size": self.size(unit),
            "last_modified": self.last_modified
        }


        if asString:
            del output['size']
            output[f"size ({unit}s)"] = self.size(unit)
            output = json.dumps({k:str(v) for (k,v) in output.items()}, indent=2)

        return output

    def __repr__(self):
        return self.details(asString=True)